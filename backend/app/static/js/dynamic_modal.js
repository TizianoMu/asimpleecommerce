function showUpdatePopup(response) {
    let data = response.data;
    let entityKey = Object.keys(data)[0];
    let formName = "add" + entityKey.charAt(0).toUpperCase() + entityKey.slice(1) +"Form"
    let entityData = response['data'][entityKey];

    // Clona il form
    let originalForm = document.getElementById(formName);
    let form = originalForm.cloneNode(true);

    // Popola dinamicamente i campi del form
    for (let key in entityData) {
        if (entityData.hasOwnProperty(key)) {
            let element = form.elements[key]; // Trova l'elemento del form con il nome corrispondente

            if (element) {
                if (element.tagName === "SELECT") {
                    // Gestisci il campo select
                    element.value = entityData[key];
                } else if (element.type === "checkbox") {
                    // Gestisci il campo checkbox (se necessario)
                    element.checked = entityData[key];
                } else {
                    // Gestisci altri tipi di campi (input di testo, ecc.)
                    element.value = entityData[key];
                }
                element.classList.add('full-width');
            }
        }
    }
    let submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        let newText = "Update " + entityKey.charAt(0).toUpperCase() + entityKey.slice(1);
        submitButton.textContent = newText;
        submitButton.classList.add('full-width');
    }
    // Gestisci l'invio del form clonato
    form.onsubmit = function (event) {
        event.preventDefault();
        let formData = new FormData(form);

        fetch(originalForm.dataset.url, {
            method: "POST",
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                console.log("Dati aggiornati:", data);
                let modal = bootstrap.Modal.getInstance(document.getElementById("dynamicModal"));
                modal.hide();
            })
            .catch(error => {
                console.error("Errore durante l'aggiornamento:", error);
            });
    };

    // Inserisci il form clonato nel modal
    let modalBody = document.querySelector("#dynamicModal .modal-body");
    modalBody.innerHTML = ""; // Pulisci eventuali contenuti precedenti
    modalBody.appendChild(form);

    // Mostra il modal
    let modal = new bootstrap.Modal(document.getElementById("dynamicModal"));
    modal.show();
}