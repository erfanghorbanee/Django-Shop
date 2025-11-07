// This script modifies the display of the phone prefix dropdown (id_phone_0) to show only the country code after selection.
// The full country name and code are restored when the dropdown is clicked for a better user experience.
document.addEventListener("DOMContentLoaded", function() {
    const phoneSelect = document.getElementById("id_phone_0");

    // Function to update the display after selection
    function updateDisplay() {
        const selectedOption = phoneSelect.options[phoneSelect.selectedIndex];
        const countryCode = selectedOption.text.match(/\+[\d]+/); // Extracts the country code
        if (countryCode) {
            phoneSelect.style.width = "auto"; // Allow the width to adjust to the content
            selectedOption.textContent = countryCode[0]; // Show only the country code
        }
    }

    // Initial update
    updateDisplay();

    // Restore full text when the dropdown is clicked
    phoneSelect.addEventListener("click", function() {
        Array.from(phoneSelect.options).forEach(option => {
            option.textContent = option.getAttribute("data-full-text") || option.textContent;
        });
    });

    // Update the display after selection
    phoneSelect.addEventListener("change", function() {
        updateDisplay();
    });
});
