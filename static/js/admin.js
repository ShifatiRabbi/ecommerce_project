$(document).ready(function() {
    // Sidebar toggle
    $('#sidebarCollapse').on('click', function() {
        $('#sidebar').toggleClass('active');
        $('#content').toggleClass('active');
    });

    // Initialize DataTables
    $('.data-table').DataTable({
        responsive: true,
        pageLength: 25,
        language: {
            search: "_INPUT_",
            searchPlaceholder: "Search..."
        }
    });

    // Update order status
    $('.update-order-status').on('change', function() {
        const orderId = $(this).data('order-id');
        const newStatus = $(this).val();
        
        $.ajax({
            url: '/admin-dashboard/ajax/update-order-status/',
            type: 'POST',
            data: {
                'order_id': orderId,
                'status': newStatus,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    showNotification('Order status updated successfully!', 'success');
                } else {
                    showNotification('Error updating order status!', 'error');
                }
            }
        });
    });

    // Update inventory
    $('.update-inventory').on('blur', function() {
        const productId = $(this).data('product-id');
        const newQuantity = $(this).val();
        
        $.ajax({
            url: '/admin-dashboard/ajax/update-inventory/',
            type: 'POST',
            data: {
                'product_id': productId,
                'quantity': newQuantity,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    showNotification('Inventory updated successfully!', 'success');
                }
            }
        });
    });

    // Dashboard charts
    function initDashboardCharts() {
        // Sales chart
        const salesCtx = document.getElementById('salesChart');
        if (salesCtx) {
            new Chart(salesCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Sales',
                        data: [12, 19, 3, 5, 2, 3],
                        borderColor: '#007bff',
                        tension: 0.1
                    }]
                }
            });
        }

        // Order status chart
        const orderCtx = document.getElementById('orderStatusChart');
        if (orderCtx) {
            new Chart(orderCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Pending', 'Processing', 'Shipped', 'Delivered'],
                    datasets: [{
                        data: [12, 19, 3, 5],
                        backgroundColor: ['#ffc107', '#17a2b8', '#007bff', '#28a745']
                    }]
                }
            });
        }
    }

    // Notification function
    function showNotification(message, type = 'info') {
        const alertClass = type === 'error' ? 'alert-danger' : 
                          type === 'success' ? 'alert-success' : 'alert-info';
        
        const notification = $('<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
                             message +
                             '<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>');
        
        $('.messages-container').append(notification);
        
        setTimeout(function() {
            notification.alert('close');
        }, 3000);
    }

    // Auto-update dashboard stats
    function updateDashboardStats() {
        $.get('/admin-dashboard/ajax/get-order-stats/', function(data) {
            $('#today-orders').text(data.today_orders);
            $('#week-orders').text(data.week_orders);
            $('#pending-orders').text(data.pending_orders);
        });
    }

    // Initialize charts and auto-update
    initDashboardCharts();
    setInterval(updateDashboardStats, 30000); // Update every 30 seconds

    // Image preview for forms
    $('.image-preview-input').on('change', function() {
        const input = $(this)[0];
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $(input).siblings('.image-preview').attr('src', e.target.result);
            }
            reader.readAsDataURL(input.files[0]);
        }
    });

    // Rich text editor initialization
    $('.rich-text-editor').each(function() {
        // Simple rich text editor - you can integrate with a proper one like TinyMCE
        $(this).css('min-height', '200px');
    });

    // Confirm before dangerous actions
    $('.confirm-action').on('click', function(e) {
        if (!confirm('Are you sure you want to perform this action?')) {
            e.preventDefault();
        }
    });
});