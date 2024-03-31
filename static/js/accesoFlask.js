function limpiarCampos(input) {
    // Regular expression to find characters that can be used in SQL injections
    var regex = /#[;'"\/\\]/g;
    // Replace matching characters with an empty string
    return input.replace(regex, '');
}

// Function to handle form submission
function submitForm() {
    // Get form data
    var formData = new FormData(document.getElementById("formFlask"));

    // Clean form data to prevent SQL injection
    for (var pair of formData.entries()) {
        formData.set(pair[0], limpiarCampos(pair[1]));
    }

    // Send AJAX request to your Flask route
    fetch('/prueba', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Check if there's an error message
        if (data.error) {
            // Display the error message using SweetAlert
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: data.error
            });
        } else if (data.errors) {
            // Handle form validation errors if any
            // You can display these errors to the user if needed
        } else {
            // Handle successful form submission
            window.location.href = "/principal";
        }
    })
    .catch(error => console.error('Error:', error));
}