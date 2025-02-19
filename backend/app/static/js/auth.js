document.addEventListener("DOMContentLoaded", function () {
    function handleFormSubmit(event, formId, apiUrl, successMessage) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const formObject = Object.fromEntries(formData.entries());
        const headers = { "Content-Type": "application/json" };

        
        if (formId !== "login-form") {
            const csrfToken = getCookie("csrf_access_token");
            if (csrfToken) {
                headers["X-CSRF-TOKEN"] = csrfToken;
            }
        } 
        axios.post(apiUrl, formObject, {
            withCredentials: true,
            headers: headers
        })
        .then(response => {
            if (successMessage) {
                document.getElementById("messages").innerHTML =
                    `<p class="success-auth-message">${successMessage}</p>`;
            } else if (response.data.redirect_url){
                // Save token in localStorage
                window.location.href = response.data.redirect_url;
            }
        })
        .catch(error => {
            document.getElementById("messages").innerHTML =
                `<p class="danger-auth-message">${error.response.data}</p>`;
        });
    }

    // Login
    const loginForm = document.querySelector("#login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", (event) => {
            handleFormSubmit(event, "login-form", loginForm.dataset.url, null);
        });
    }

    // Register
    const registerForm = document.querySelector("#register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", (event) => {
            handleFormSubmit(event, "register-form", registerForm.dataset.url,
                `Registration successful! <a href="${registerForm.dataset.loginUrl}">Go to Login</a>`);
        });
    }
});
