// JavaScript for Product Detail Page
document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const mainImage = document.getElementById('mainImage');
    const addToCartButton = document.getElementById('addToCartButton');
    const quantityInput = document.getElementById('productQuantity');
    const decreaseBtn = document.getElementById('decreaseQuantity');
    const increaseBtn = document.getElementById('increaseQuantity');
    const thumbnails = document.querySelectorAll('.thumbnail');
    
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
        addToCartButton.addEventListener('click', () => {
            // Get product data
            const productSlug = window.location.pathname.split('/').filter(item => item).pop();
            const quantity = parseInt(quantityInput?.value || 1);
            
            // Prepare feedback to user
            const originalText = addToCartButton.innerHTML;
            addToCartButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Adding...';
            addToCartButton.disabled = true;
            
            // Simulate API call (replace with actual fetch when ready)
            setTimeout(() => {
                // Show success
                addToCartButton.innerHTML = '<i class="bi bi-check-lg"></i> Added to Cart';
                addToCartButton.classList.remove('btn-primary');
                addToCartButton.classList.add('btn-success');
                
                // Reset button after delay
                setTimeout(() => {
                    addToCartButton.innerHTML = originalText;
                    addToCartButton.classList.remove('btn-success');
                    addToCartButton.classList.add('btn-primary');
                    addToCartButton.disabled = false;
                }, 1500);
                
                // Here you would integrate with an actual cart API
                console.log(`Added product ${productSlug} to cart with quantity: ${quantity}`);
                
                // Dispatch a custom event that other parts of the app can listen for
                const cartEvent = new CustomEvent('cart:updated', {
                    detail: { productSlug, quantity, action: 'add' }
                });
                document.dispatchEvent(cartEvent);
            }, 800);
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
});
