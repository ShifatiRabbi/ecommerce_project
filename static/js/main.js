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