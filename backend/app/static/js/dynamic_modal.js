// Function to clone the form and add the event listener
function cloneFormAndAddListener(formName, editformName, dataUrl) {
    let originalForm = document.getElementById(formName);
    let form = originalForm.cloneNode(true);
    form.id = editformName;
    form.method = 'POST';
    form.dataset.url = dataUrl;
    form.classList.remove('d-none')
    form.removeAttribute("onsubmit"); // Remove any pre-existing onsubmit attributes

    // Add the submit event listener to the cloned form
    form.addEventListener("submit", (event) => {
        handleFormSubmit(event, editformName, form.dataset.url, form.dataset.successMessage, 'POST', null, '');
    });

    return form; // Return the cloned form
}

function showUpdatePopup(response,dataUrl) {
    let data = response.data;
    let entityKey = Object.keys(data)[0];
    let formName = "add" + entityKey.charAt(0).toUpperCase() + entityKey.slice(1) +"Form"
    let editformName = "edit" + entityKey.charAt(0).toUpperCase() + entityKey.slice(1) +"Form"
    let entityData = response['data'][entityKey];

    // Clone the form
    let form = cloneFormAndAddListener(formName, editformName, dataUrl);
    
    // Set form fields dinamically
    for (let key in entityData) {
        if (entityData.hasOwnProperty(key)) {
            let element = form.elements[key];

            if (element) {
                if (element.tagName === "SELECT") {
                    element.value = entityData[key];
                } else if (element.type === "checkbox") {
                    element.checked = entityData[key];
                } else {
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

    // Set form in modal
    let modalBody = document.querySelector("#dynamicModal .modal-body");
    modalBody.innerHTML = ""; // Clear modal
    modalBody.appendChild(form);

    // Show Modal
    let modal = new bootstrap.Modal(document.getElementById("dynamicModal"));
    modal._element.addEventListener('shown.bs.modal',function(){
        // Set focus on first input with delay
        const inputs = form.querySelectorAll("input, textarea, select");
        for (const input of inputs) {
            if (!input.disabled) {
                input.focus();
                break;
            }
        }
    })
    modal.show();

    
}