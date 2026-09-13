from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

load_dotenv()  # charge les variables définies dans le fichier .env

app = Flask(__name__)

# Fichier où on stocke les messages reçus (au lieu d'une vraie base de données pour rester simple)
MESSAGES_FILE = "messages.json"

# --- Configuration email ---
# On lit ces valeurs depuis des variables d'environnement : on ne met JAMAIS
# un mot de passe directement dans le code (encore moins si le code est publié sur GitHub).
SMTP_SERVEUR = os.environ.get("SMTP_SERVEUR", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")          # ton adresse d'envoi
SMTP_MOT_DE_PASSE = os.environ.get("SMTP_MOT_DE_PASSE")  # mot de passe d'application
EMAIL_DESTINATAIRE = os.environ.get("EMAIL_DESTINATAIRE", SMTP_EMAIL)  # où recevoir les demandes


def envoyer_email(nom, email_client, message):
    """Envoie un email récapitulatif à EMAIL_DESTINATAIRE. Renvoie True/False."""
    if not SMTP_EMAIL or not SMTP_MOT_DE_PASSE:
        print("Configuration SMTP manquante : email non envoyé (message quand même sauvegardé).")
        return False

    contenu = f"Nouveau message depuis le site InfoRépar\n\nNom : {nom}\nEmail : {email_client}\n\nMessage :\n{message}"

    email_msg = MIMEText(contenu, "plain", "utf-8")
    email_msg["Subject"] = f"Nouvelle demande de {nom} - InfoRépar"
    email_msg["From"] = SMTP_EMAIL
    email_msg["To"] = EMAIL_DESTINATAIRE
    email_msg["Reply-To"] = email_client  # pour pouvoir répondre directement au client

    try:
        with smtplib.SMTP(SMTP_SERVEUR, SMTP_PORT) as serveur:
            serveur.starttls()  # connexion chiffrée
            serveur.login(SMTP_EMAIL, SMTP_MOT_DE_PASSE)
            serveur.send_message(email_msg)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")
        return False


def lire_messages():
    """Lit les messages déjà enregistrés, ou renvoie une liste vide."""
    if not os.path.exists(MESSAGES_FILE):
        return []
    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder_message(message):
    """Ajoute un nouveau message au fichier JSON."""
    messages = lire_messages()
    messages.append(message)
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


@app.route("/")
def accueil():
    """Affiche la page principale du site."""
    return render_template("index.html")


@app.route("/api/contact", methods=["POST"])
def contact():
    """Reçoit les données du formulaire de contact en JSON."""
    data = request.get_json()

    nom = data.get("nom", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    # Validation basique côté serveur (ne jamais faire confiance au frontend seul)
    if not nom or not email or not message:
        return jsonify({"succes": False, "erreur": "Tous les champs sont obligatoires."}), 400

    nouveau_message = {
        "nom": nom,
        "email": email,
        "message": message,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    sauvegarder_message(nouveau_message)
    print(f"Nouveau message reçu de {nom} ({email})")

    email_envoye = envoyer_email(nom, email, message)

    return jsonify({
        "succes": True,
        "message": "Message bien reçu !" if email_envoye else "Message enregistré (email non envoyé, vérifie la configuration SMTP).",
    })


@app.route("/api/messages")
def voir_messages():
    """Route pratique pour consulter les messages reçus (à protéger dans un vrai projet)."""
    return jsonify(lire_messages())


if __name__ == "__main__":
    app.run(debug=True)
  
