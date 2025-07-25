
document.addEventListener("DOMContentLoaded", function() {
    const addSlotForm = document.getElementById("addSlotForm");

    if (addSlotForm) {
        addSlotForm.addEventListener("submit", function(event) {
            const numberOfSlots = document.getElementById("number_of_slots").value;
            if (numberOfSlots <= 0) {
                alert("Please enter a valid number of slots.");
                event.preventDefault();
            }
        });
    }

    const passwordInput = document.getElementById("password");
    const togglePasswordButton = document.getElementById("togglePassword");

    if (passwordInput && togglePasswordButton) {
        togglePasswordButton.addEventListener("click", function() {
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                togglePasswordButton.textContent = "Hide Password";
            } else {
                passwordInput.type = "password";
                togglePasswordButton.textContent = "Show Password";
            }
        });
    }
});
