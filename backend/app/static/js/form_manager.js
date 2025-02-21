document.addEventListener("DOMContentLoaded", function () {

    function handleFormSubmit(event, formId, apiUrl, successMessage, method = "POST", callbackName = null) {
        event.preventDefault(); // Prevent the default form submission behavior

        let formData = new FormData(event.target);
        let formObject = Object.fromEntries(formData.entries()); // Convert form data to an object
        let headers = { "Content-Type": "application/json" };

        // Exclude CSRF token for login form
        if (formId !== "login-form") {
            const csrfToken = getCookie("csrf_access_token");
            if (csrfToken) {
                headers["X-CSRF-TOKEN"] = csrfToken;
            }
        }

        let axiosConfig = {
            withCredentials: true, // Ensure credentials (cookies) are sent with the request
            headers: headers,
        };

        let axiosCall;
        if (method === "POST") {
            axiosCall = axios.post(apiUrl, formObject, axiosConfig);
        } else if (method === "GET") {
            axiosConfig.params = formObject; // Pass form data as query parameters for GET requests
            axiosCall = axios.get(apiUrl, axiosConfig);
            if (headers["Content-Type"]) delete headers["Content-Type"]; // Remove JSON header for GET requests
        }

        axiosCall
            .then(response => {
                if (successMessage) {
                    // Display success message and reset form
                    document.getElementById("messages").innerHTML =
                        `<p class="success-auth-message">${successMessage}</p>`;
                    document.getElementById(formId).reset();
                } else if (response.data.redirect_url) {
                    // Redirect if a URL is provided in the response
                    window.location.href = response.data.redirect_url;
                } else if (response.data) {
                    console.log("GET response:", response.data); // Log response data for debugging
                }
                if (callbackName && typeof window[callbackName] === "function") {
                    window[callbackName](response); // Esegui la funzione callback
                }
            })
            .catch(error => {
                // Display error message if request fails
                document.getElementById("messages").innerHTML =
                    `<p class="danger-auth-message">${error.response?.data?.error || "An error occurred."}</p>`;
            });
    }

    // Attach event listener to all forms with `data-url` attribute
    document.querySelectorAll("form[data-url]").forEach(form => {
        const method = form.dataset.method || "POST"; // Default: POST
        const callbackName = form.dataset.callback || null; // Default: POST
        form.addEventListener("submit", (event) =>
            handleFormSubmit(
                event, 
                form.getAttribute("id"), 
                form.dataset.url, 
                form.dataset.successMessage, 
                method,
                callbackName)
        );
    });
});
