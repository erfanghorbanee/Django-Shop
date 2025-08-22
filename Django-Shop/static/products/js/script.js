document.addEventListener('DOMContentLoaded', () => {
    let currentPage = 1;
    let loading = false;
    const spinner = document.getElementById('loading-spinner');
    const container = document.getElementById('products-container');
    let hasMore = container.dataset.hasMore === "true";

    // Throttled Scroll Event Listener for Efficiency
    const onScroll = throttle(() => {
        if (isNearBottom() && !loading) {
            fetchMoreProducts();
        }
    }, 200);
    window.addEventListener('scroll', onScroll); // Throttle time set to 200ms

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
    if (!hasMore) return;
    loading = true;
    spinner.classList.remove('d-none');
    const nextPage = currentPage + 1;

        try {
            const url = getUrlWithUpdatedParams(nextPage);
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) throw new Error(`Failed to load page ${currentPage}.`);

            const html = await response.text();
            if (html.trim()) {
                container.insertAdjacentHTML('beforeend', html);
                // advance currentPage only after successful insert
                currentPage = nextPage;
                // Count how many product items were just fetched
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                const fetchedItems = tempDiv.querySelectorAll('.product-item').length;
                console.log('Fetched HTML:', html);
                console.log('Fetched product items:', fetchedItems);
                if (fetchedItems < 12) {
                    hasMore = false;
                    window.removeEventListener('scroll', onScroll);
                }
            } else {
                hasMore = false;
                window.removeEventListener('scroll', onScroll);
            }
        } catch (error) {
            // Suppress error if it's just a missing page
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
