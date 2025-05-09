// JavaScript for Product Detail Page
document.addEventListener('DOMContentLoaded', () => {
    const mainImage = document.getElementById('mainImage');
    const addToCartButton = document.getElementById('addToCartButton');

    window.changeMainImage = function(imageUrl) {
        mainImage.src = imageUrl;
    };

    addToCartButton.addEventListener('click', () => {
        alert("This feature is coming soon!");
    });
});
