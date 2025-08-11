// JavaScript for Product Detail Page
document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const mainImage = document.getElementById('mainImage');
    const addToCartButton = document.getElementById('addToCartButton');
    const quantityInput = document.getElementById('productQuantity');
    const decreaseBtn = document.getElementById('decreaseQuantity');
    const increaseBtn = document.getElementById('increaseQuantity');
    const thumbnails = document.querySelectorAll('.thumbnail');
    const starRatingInputs = document.querySelectorAll('.star-rating input');
    const starRatingLabels = document.querySelectorAll('.star-rating label');
    
    // Change main image on thumbnail click
    window.changeMainImage = function(imageUrl) {
        // Add fade-out effect
        mainImage.style.opacity = '0.5';
        
        // Change image and fade back in
        setTimeout(() => {
            mainImage.src = imageUrl;
            mainImage.style.opacity = '1';
            
            // Update active thumbnail
            thumbnails.forEach(thumb => {
                if (thumb.src === imageUrl) {
                    thumb.classList.add('active');
                } else {
                    thumb.classList.remove('active');
                }
            });
        }, 200);
    };
    
    // Quantity controls
    if (decreaseBtn && increaseBtn && quantityInput) {
        // Get maximum from input or set default
        const maxQuantity = parseInt(quantityInput.getAttribute('max')) || 10;
        
        // Decrease quantity
        decreaseBtn.addEventListener('click', () => {
            const currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });
        
        // Increase quantity
        increaseBtn.addEventListener('click', () => {
            const currentValue = parseInt(quantityInput.value);
            if (currentValue < maxQuantity) {
                quantityInput.value = currentValue + 1;
            }
        });
        
        // Validate manual input
        quantityInput.addEventListener('change', () => {
            let value = parseInt(quantityInput.value);
            
            // Handle invalid values
            if (isNaN(value) || value < 1) {
                value = 1;
            } else if (value > maxQuantity) {
                value = maxQuantity;
            }
            
            quantityInput.value = value;
        });
    }
    
    // Add to Cart functionality
    if (addToCartButton) {
        const form = document.getElementById('addToCartForm');
        addToCartButton.addEventListener('click', (e) => {
            if(!form) return;
            e.preventDefault();
            const quantity = parseInt(quantityInput?.value || 1);
            const originalHTML = addToCartButton.innerHTML;
            addToCartButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Adding...';
            addToCartButton.disabled = true;
            // sync hidden qty (server still handles gracefully)
            const hiddenQty = document.getElementById('addToCartHiddenQty');
            if (hiddenQty) hiddenQty.value = quantity;

            fetch(form.action, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken(), 'X-Requested-With': 'XMLHttpRequest' },
                body: new URLSearchParams(new FormData(form))
            })
            .then(r => r.json().catch(() => null))
            .then(data => {
                if (data && data.ok) {
                    addToCartButton.innerHTML = '<i class="bi bi-check-lg"></i> Added';
                    addToCartButton.classList.remove('btn-primary');
                    addToCartButton.classList.add('btn-success');
                    // update badge
                    const badge = document.getElementById('cartBadgeCount');
                    if (badge && data.total_quantity !== undefined) {
                        badge.textContent = data.total_quantity;
                        if (data.total_quantity > 0) badge.classList.remove('d-none');
                    }
                } else {
                    addToCartButton.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Error';
                    addToCartButton.classList.remove('btn-primary');
                    addToCartButton.classList.add('btn-danger');
                }
                setTimeout(() => {
                    addToCartButton.innerHTML = originalHTML;
                    addToCartButton.classList.remove('btn-success','btn-danger');
                    addToCartButton.classList.add('btn-primary');
                    addToCartButton.disabled = false;
                }, 1600);
            })
            .catch(() => {
                addToCartButton.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Error';
                addToCartButton.classList.remove('btn-primary');
                addToCartButton.classList.add('btn-danger');
                setTimeout(() => {
                    addToCartButton.innerHTML = originalHTML;
                    addToCartButton.classList.remove('btn-danger');
                    addToCartButton.classList.add('btn-primary');
                    addToCartButton.disabled = false;
                }, 1600);
            });
        });
    }
    
    // Initialize zoom effect on main image
    if (mainImage) {
        const imageContainer = mainImage.parentElement;
        
        mainImage.addEventListener('mousemove', (e) => {
            // Only apply zoom effect on larger screens
            if (window.innerWidth < 992) return;
            
            const { left, top, width, height } = imageContainer.getBoundingClientRect();
            const x = (e.clientX - left) / width;
            const y = (e.clientY - top) / height;
            
            mainImage.style.transformOrigin = `${x * 100}% ${y * 100}%`;
            mainImage.style.transform = 'scale(1.5)';
        });
        
        mainImage.addEventListener('mouseleave', () => {
            mainImage.style.transform = 'scale(1)';
        });
    }
    
    // Star Rating functionality
    if (starRatingInputs.length && starRatingLabels.length) {
        // Initialize rating UI
        const updateStarDisplay = (rating) => {
            starRatingLabels.forEach((label, index) => {
                // The labels are in reverse order in the HTML (5 to 1)
                const starValue = 5 - index;
                if (starValue <= rating) {
                    label.querySelector('i').classList.add('text-warning');
                } else {
                    label.querySelector('i').classList.remove('text-warning');
                }
            });
        };
        
        // Handle clicking on stars
        starRatingLabels.forEach(label => {
            label.addEventListener('click', () => {
                const rating = label.getAttribute('for').replace('rating', '');
                document.getElementById(`rating${rating}`).checked = true;
                updateStarDisplay(rating);
            });
            
            // Hover effects
            label.addEventListener('mouseenter', () => {
                const rating = label.getAttribute('for').replace('rating', '');
                updateStarDisplay(rating);
            });
            
            label.addEventListener('mouseleave', () => {
                // When mouse leaves, show the selected rating
                const selectedRating = Array.from(starRatingInputs).find(input => input.checked)?.value || 0;
                updateStarDisplay(selectedRating);
            });
        });
    }
    
    // Review deletion confirmation
    const reviewDeleteForms = document.querySelectorAll('form[action*="delete_review"]');
    reviewDeleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete your review?')) {
                e.preventDefault();
            }
        });
    });
    
    // Show success messages with fade effect
    const messages = document.querySelectorAll('.alert');
    if (messages.length) {
        messages.forEach(message => {
            setTimeout(() => {
                message.style.transition = 'opacity 0.5s ease';
                message.style.opacity = '0';
                
                setTimeout(() => {
                    message.remove();
                }, 500);
            }, 5000);
        });
    }

    // Wishlist Toggle AJAX
    const wishlistBtn = document.getElementById('wishlistToggleBtn');
    const wishlistIcon = document.getElementById('wishlistHeartIcon');
    if (wishlistBtn && wishlistIcon) {
        wishlistBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const productId = wishlistBtn.getAttribute('data-product-id');
            fetch('/users/api/v1/wishlist/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added') {
                    wishlistIcon.classList.remove('bi-heart');
                    wishlistIcon.classList.add('bi-heart-fill');
                } else if (data.status === 'removed') {
                    wishlistIcon.classList.remove('bi-heart-fill');
                    wishlistIcon.classList.add('bi-heart');
                }
            })
            .catch(error => {
                console.error('Wishlist toggle failed:', error);
            });
        });
    }

    // Helper to get CSRF token from cookie
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
