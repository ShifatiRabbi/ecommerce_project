$(document).ready(function() {
    // Language switcher
    $('.change-language').on('click', function(e) {
        e.preventDefault();
        const lang = $(this).data('lang');
        
        $.ajax({
            url: '/change-language/',
            type: 'POST',
            data: {
                'language': lang,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    location.reload();
                }
            }
        });
    });
    
    // Add to cart
    $('.add-to-cart').on('click', function() {
        const button = $(this);
        const productId = button.data('product-id');
        const quantity = button.data('quantity') || 1;
        
        button.prop('disabled', true).addClass('loading');
        
        $.ajax({
            url: '/cart/add/',
            type: 'POST',
            data: {
                'product_id': productId,
                'quantity': quantity,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Update cart count
                    $('.cart-badge').text(response.cart_total_items);
                    
                    // Show success message
                    showMessage(response.message, 'success');
                }
            },
            complete: function() {
                button.prop('disabled', false).removeClass('loading');
            }
        });
    });
    
    // Search functionality
    $('#search-input').on('input', function() {
        const query = $(this).val();
        if (query.length > 2) {
            $.get('/shop/search/', {q: query}, function(data) {
                // Handle search results
                console.log(data);
            });
        }
    });
    
    // Show message function
    function showMessage(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const alert = $('<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
                       message +
                       '<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>');
        
        $('#messages-container').html(alert);
        
        setTimeout(function() {
            alert.alert('close');
        }, 3000);
    }
});

// Main JavaScript File
$(document).ready(function() {
    // Initialize all functions
    initBackToTop();
    initSearchFunctionality();
    initLanguageSwitcher();
    initMobileMenu();
    initSmoothScrolling();
    initCartFunctionality();
    initHeaderEffects();
    initFormValidations();
    initLazyLoading();
    initPerformanceOptimizations();
});

// Back to Top Button
function initBackToTop() {
    const backToTop = $('#backToTop');
    
    $(window).on('scroll', function() {
        if ($(this).scrollTop() > 300) {
            backToTop.addClass('show');
        } else {
            backToTop.removeClass('show');
        }
    });
    
    backToTop.on('click', function() {
        $('html, body').animate({ scrollTop: 0 }, 500);
        return false;
    });
}

// Search Functionality
function initSearchFunctionality() {
    // Search toggle for mobile
    $('.search-toggle').on('click', function() {
        $('.search-overlay, .mobile-search-overlay').addClass('show');
        $('.search-overlay input, .mobile-search-overlay input').focus();
    });
    
    // Close search overlay
    $('.search-close').on('click', function() {
        $('.search-overlay, .mobile-search-overlay').removeClass('show');
    });
    
    // Close on ESC key
    $(document).on('keyup', function(e) {
        if (e.key === 'Escape') {
            $('.search-overlay, .mobile-search-overlay').removeClass('show');
        }
    });
    
    // Search form submission
    $('.search-form').on('submit', function(e) {
        const searchTerm = $(this).find('input[name="search"]').val().trim();
        if (searchTerm === '') {
            e.preventDefault();
            $(this).find('input[name="search"]').focus();
        }
    });
}

// Language Switcher
function initLanguageSwitcher() {
    $('.change-language').on('click', function(e) {
        e.preventDefault();
        const lang = $(this).data('lang');
        
        $.ajax({
            url: '/change-language/',
            type: 'POST',
            data: {
                'language': lang,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    location.reload();
                }
            },
            error: function() {
                showNotification('Error changing language', 'error');
            }
        });
    });
}

// Mobile Menu
function initMobileMenu() {
    // Close mobile menu when clicking on a link
    $('.navbar-nav .nav-link').on('click', function() {
        $('.navbar-collapse').collapse('hide');
    });
    
    // Handle dropdowns on touch devices
    if ('ontouchstart' in window) {
        $('.dropdown-toggle').on('click', function(e) {
            if (!$(this).parent().hasClass('show')) {
                e.preventDefault();
                $(this).dropdown('toggle');
            }
        });
    }
}

// Smooth Scrolling
function initSmoothScrolling() {
    $('a[href^="#"]').on('click', function(e) {
        if (this.hash !== '') {
            e.preventDefault();
            const hash = this.hash;
            
            $('html, body').animate({
                scrollTop: $(hash).offset().top - 80
            }, 800, function() {
                window.location.hash = hash;
            });
        }
    });
}

// Cart Functionality
function initCartFunctionality() {
    // Update cart count
    function updateCartCount(count) {
        $('.cart-count').text(count);
    }
    
    // Add to cart
    $('.add-to-cart').on('click', function() {
        const productId = $(this).data('product-id');
        const quantity = $(this).data('quantity') || 1;
        const button = $(this);
        
        button.prop('disabled', true).addClass('loading');
        
        $.ajax({
            url: '/cart/add/',
            type: 'POST',
            data: {
                'product_id': productId,
                'quantity': quantity,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    updateCartCount(response.cart_total_items);
                    showNotification(response.message, 'success');
                    
                    // Add animation to cart icon
                    $('.fa-shopping-cart').parent().addClass('pulse');
                    setTimeout(() => {
                        $('.fa-shopping-cart').parent().removeClass('pulse');
                    }, 1000);
                } else {
                    showNotification(response.message, 'error');
                }
            },
            error: function() {
                showNotification('Error adding product to cart', 'error');
            },
            complete: function() {
                button.prop('disabled', false).removeClass('loading');
            }
        });
    });
}

// Header Effects
function initHeaderEffects() {
    let lastScrollTop = 0;
    const header = $('.main-header');
    const headerHeight = header.outerHeight();
    
    $(window).on('scroll', function() {
        const scrollTop = $(this).scrollTop();
        
        // Sticky header
        if (scrollTop > headerHeight) {
            header.addClass('sticky-header');
        } else {
            header.removeClass('sticky-header');
        }
        
        // Hide/show header on scroll
        if (scrollTop > lastScrollTop && scrollTop > headerHeight) {
            // Scrolling down
            header.addClass('header-hidden');
        } else {
            // Scrolling up
            header.removeClass('header-hidden');
        }
        
        lastScrollTop = scrollTop;
    });
}

// Form Validations
function initFormValidations() {
    // Contact form validation
    $('#contact-form').on('submit', function(e) {
        let isValid = true;
        const form = $(this);
        
        form.find('input[required], textarea[required]').each(function() {
            if ($(this).val().trim() === '') {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        // Email validation
        const email = form.find('input[type="email"]');
        if (email.val() && !isValidEmail(email.val())) {
            isValid = false;
            email.addClass('is-invalid');
        }
        
        if (!isValid) {
            e.preventDefault();
            showNotification('Please fill all required fields correctly', 'error');
        }
    });
    
    // Newsletter form
    $('.newsletter-form').on('submit', function(e) {
        e.preventDefault();
        const email = $(this).find('input[type="email"]');
        
        if (!isValidEmail(email.val())) {
            email.addClass('is-invalid');
            showNotification('Please enter a valid email address', 'error');
            return;
        }
        
        email.removeClass('is-invalid');
        
        // Simulate subscription
        const button = $(this).find('button[type="submit"]');
        const originalText = button.html();
        
        button.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i> Subscribing...');
        
        setTimeout(() => {
            showNotification('Thank you for subscribing to our newsletter!', 'success');
            $(this)[0].reset();
            button.prop('disabled', false).html(originalText);
        }, 1500);
    });
}

// Lazy Loading
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Performance Optimizations
function initPerformanceOptimizations() {
    // Debounce function for scroll events
    function debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }
    
    // Throttle function for resize events
    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // Optimize scroll events
    const optimizedScroll = debounce(function() {
        // Scroll-related code here
    }, 10);
    
    $(window).on('scroll', optimizedScroll);
    
    // Optimize resize events
    const optimizedResize = throttle(function() {
        // Resize-related code here
    }, 100);
    
    $(window).on('resize', optimizedResize);
}

// Utility Functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// ✅ Reusable Bootstrap Notification
function showNotification(message, type = 'info') {
    // Define alert class and icon based on type
    const alertClass =
        type === 'success' ? 'alert-success' :
        type === 'error'   ? 'alert-danger'  :
        type === 'warning' ? 'alert-warning' : 'alert-info';

    const icon =
        type === 'success' ? 'check-circle' :
        type === 'error'   ? 'exclamation-triangle' :
        type === 'warning' ? 'exclamation-circle' : 'info-circle';

    // Create the alert element
    const notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3 shadow-lg"
             style="z-index: 9999; min-width: 320px; max-width: 600px;"
             role="alert">
            <i class="fas fa-${icon} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);

    // Append to body
    $('body').append(notification);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        notification.alert('close');
    }, 5000);
}