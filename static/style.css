document.getElementById("contact-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const nom = document.getElementById("nom").value;
  const email = document.getElementById("email").value;
  const message = document.getElementById("message").value;

  const confirmation = document.getElementById("confirmation");

  try {
    const reponse = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nom, email, message }),
    });

    const resultat = await reponse.json();

    if (resultat.succes) {
      confirmation.textContent = "Merci ! Votre message a bien été envoyé.";
      confirmation.style.color = "green";
      this.reset();
    } else {
      confirmation.textContent = "Erreur : " + resultat.erreur;
      confirmation.style.color = "red";
    }
  } catch (erreur) {
    confirmation.textContent = "Impossible de contacter le serveur.";
    confirmation.style.color = "red";
    console.error(erreur);
  }

  confirmation.classList.remove("hidden");
});
