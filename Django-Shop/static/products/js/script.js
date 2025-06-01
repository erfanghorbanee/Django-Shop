document.addEventListener('DOMContentLoaded', () => {
    let currentPage = 1;
    let loading = false;
    const spinner = document.getElementById('loading-spinner');
    const container = document.getElementById('products-container');

    // Throttled Scroll Event Listener for Efficiency
    window.addEventListener('scroll', throttle(() => {
        if (isNearBottom() && !loading) {
            fetchMoreProducts();
        }
    }, 200)); // Throttle time set to 200ms

    function throttle(callback, delay) {
        let throttleTimeout;
        return function () {
            if (throttleTimeout) return;
            throttleTimeout = setTimeout(() => {
                callback();
                throttleTimeout = null;
            }, delay);
        };
    }

    function isNearBottom() {
        return window.innerHeight + window.scrollY >= document.body.offsetHeight - 500;
    }

    function getUrlWithUpdatedParams(page) {
        // Get current URL and parse its query parameters
        const url = new URL(window.location.href);
        const searchParams = url.searchParams;
        
        // Update or add the page parameter
        searchParams.set('page', page);
        
        // Return only the path and query params (not the full URL)
        return `${url.pathname}${url.search}`;
    }

    async function fetchMoreProducts() {
        loading = true;
        spinner.classList.remove('d-none');
        currentPage++;

        try {
            // Get URL with all current query parameters plus updated page
            const url = getUrlWithUpdatedParams(currentPage);
            const response = await fetch(url);
            
            if (!response.ok) throw new Error(`Failed to load page ${currentPage}.`);

            const html = await response.text();
            if (html.trim()) {
                container.insertAdjacentHTML('beforeend', html);
            } else {
                console.warn("No more products available.");
                window.removeEventListener('scroll', fetchMoreProducts);
            }
        } catch (error) {
            console.error(`Error fetching products: ${error.message}`);
        } finally {
            loading = false;
            spinner.classList.add('d-none');
        }
    }

    // Wishlist Toggle AJAX for product list and related products
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

    document.querySelectorAll('.wishlist-toggle-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = btn.getAttribute('data-product-id');
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
                // Find the heart icon for this product
                const heartIcon = document.querySelector('.wishlist-heart-icon[data-product-id="' + productId + '"]');
                if (data.status === 'added') {
                    heartIcon.classList.remove('bi-heart');
                    heartIcon.classList.add('bi-heart-fill');
                } else if (data.status === 'removed') {
                    heartIcon.classList.remove('bi-heart-fill');
                    heartIcon.classList.add('bi-heart');
                }
            })
            .catch(error => {
                console.error('Wishlist toggle failed:', error);
            });
        });
    });
});
