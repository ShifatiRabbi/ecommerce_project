// Admin Dashboard Main JavaScript
$(document).ready(function() {
    // Sidebar toggle with animation
    $('#sidebarCollapse').on('click', function() {
        $('#sidebar').toggleClass('active');
        $('#content').toggleClass('active');
        $(this).find('i').toggleClass('fa-align-left fa-align-right');
        
        // Store sidebar state in localStorage
        const isCollapsed = $('#sidebar').hasClass('active');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
    });

    // Restore sidebar state
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        $('#sidebar').addClass('active');
        $('#content').addClass('active');
        $('#sidebarCollapse i').toggleClass('fa-align-left fa-align-right');
    }

    // Initialize DataTables with enhanced options
    $('.data-table').DataTable({
        responsive: true,
        pageLength: 25,
        ordering: true,
        language: {
            search: "_INPUT_",
            searchPlaceholder: "Search...",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            infoEmpty: "Showing 0 to 0 of 0 entries",
            infoFiltered: "(filtered from _MAX_ total entries)",
            paginate: {
                first: "First",
                last: "Last",
                next: "Next",
                previous: "Previous"
            }
        },
        dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
             '<"row"<"col-sm-12"tr>>' +
             '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
        initComplete: function() {
            // Add custom class to search input
            $('.dataTables_filter input').addClass('form-control form-control-sm');
            $('.dataTables_length select').addClass('form-select form-select-sm');
        }
    });

    // Auto-update dashboard stats
    function updateDashboardStats() {
        $.ajax({
            url: '/admin-dashboard/ajax/get-order-stats/',
            type: 'GET',
            success: function(data) {
                $('#today-orders').text(data.today_orders);
                $('#pending-orders').text(data.pending_orders);
                $('#weekly-revenue').text('৳' + data.total_revenue.toLocaleString());
                
                // Update badge with animation
                $('.badge').addClass('pulse');
                setTimeout(() => $('.badge').removeClass('pulse'), 1000);
            }
        });
    }

    // Update stats every 2 minutes
    setInterval(updateDashboardStats, 120000);

    // Enhanced notification system
    window.showNotification = function(message, type = 'info', duration = 5000) {
        const alertClass = type === 'error' ? 'alert-danger' : 
                          type === 'success' ? 'alert-success' : 
                          type === 'warning' ? 'alert-warning' : 'alert-info';
        
        const icon = type === 'success' ? 'check' : 
                    type === 'error' ? 'exclamation-triangle' : 
                    type === 'warning' ? 'exclamation-circle' : 'info';
        
        const notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show slide-in" role="alert">
                <i class="fas fa-${icon} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        // Remove existing notifications
        $('.alert-dismissible').alert('close');
        
        // Add new notification
        $('.messages-container').html(notification);
        
        // Auto-remove after duration
        setTimeout(() => notification.alert('close'), duration);
        
        // Add sound for important notifications
        if (type === 'error' || type === 'success') {
            // You can add notification sounds here
        }
    }

    // Confirm before dangerous actions
    $('.confirm-action').on('click', function(e) {
        e.preventDefault();
        const message = $(this).data('confirm') || 'Are you sure you want to perform this action?';
        const href = $(this).attr('href');
        
        Swal.fire({
            title: 'Confirm Action',
            text: message,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, proceed!',
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                if (href) {
                    window.location.href = href;
                } else {
                    // For form submissions
                    $(this).closest('form').submit();
                }
            }
        });
    });

    // Auto-save forms
    $('.auto-save').on('input', function() {
        const form = $(this).closest('form');
        clearTimeout(window.autoSaveTimeout);
        window.autoSaveTimeout = setTimeout(() => {
            $.ajax({
                url: form.attr('action'),
                type: 'POST',
                data: form.serialize(),
                success: function() {
                    showNotification('Changes saved automatically', 'success', 2000);
                }
            });
        }, 2000);
    });

    // Image preview and upload
    $('.image-preview-input').on('change', function() {
        const input = $(this)[0];
        const preview = $(this).siblings('.image-preview');
        
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.html(`<img src="${e.target.result}" class="img-fluid rounded" alt="Preview">`);
            };
            reader.readAsDataURL(input.files[0]);
        }
    });

    // Rich text editor initialization
    $('.rich-text-editor').each(function() {
        // Simple implementation - integrate with a proper editor like TinyMCE or CKEditor
        $(this).css('min-height', '200px');
        
        // Add toolbar for basic formatting
        const toolbar = $(`
            <div class="rich-text-toolbar btn-toolbar mb-2">
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-outline-secondary" data-command="bold"><i class="fas fa-bold"></i></button>
                    <button type="button" class="btn btn-outline-secondary" data-command="italic"><i class="fas fa-italic"></i></button>
                    <button type="button" class="btn btn-outline-secondary" data-command="underline"><i class="fas fa-underline"></i></button>
                </div>
                <div class="btn-group btn-group-sm ms-2">
                    <button type="button" class="btn btn-outline-secondary" data-command="insertUnorderedList"><i class="fas fa-list-ul"></i></button>
                    <button type="button" class="btn btn-outline-secondary" data-command="insertOrderedList"><i class="fas fa-list-ol"></i></button>
                </div>
            </div>
        `);
        
        $(this).before(toolbar);
        
        toolbar.find('button').on('click', function() {
            const command = $(this).data('command');
            document.execCommand(command, false, null);
            $(this).closest('.rich-text-editor').focus();
        });
    });

    // Keyboard shortcuts
    $(document).on('keydown', function(e) {
        // Ctrl + S to save
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            $('form:focus').submit();
        }
        
        // Ctrl + D for dashboard
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            window.location.href = '/admin-dashboard/';
        }
        
        // Ctrl + / for help
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            showKeyboardShortcuts();
        }
    });

    // Search functionality with debounce
    let searchTimeout;
    $('.live-search').on('input', function() {
        clearTimeout(searchTimeout);
        const searchTerm = $(this).val();
        const table = $(this).data('table');
        
        searchTimeout = setTimeout(() => {
            if (searchTerm.length > 2 || searchTerm.length === 0) {
                $(`#${table}`).DataTable().search(searchTerm).draw();
            }
        }, 500);
    });

    // Bulk actions
    $('.select-all').on('change', function() {
        const isChecked = $(this).is(':checked');
        $(this).closest('table').find('.select-item').prop('checked', isChecked);
    });

    $('.bulk-action-btn').on('click', function() {
        const action = $(this).data('action');
        const selectedItems = $('.select-item:checked');
        
        if (selectedItems.length === 0) {
            showNotification('Please select at least one item', 'warning');
            return;
        }
        
        const itemIds = selectedItems.map(function() {
            return $(this).val();
        }).get();
        
        // Perform bulk action via AJAX
        $.ajax({
            url: '/admin-dashboard/ajax/bulk-action/',
            type: 'POST',
            data: {
                action: action,
                items: itemIds,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    showNotification(`${selectedItems.length} items ${action}ed successfully`, 'success');
                    // Reload or update table
                    location.reload();
                }
            }
        });
    });

    // Real-time stock updates
    $('.stock-input').on('blur', function() {
        const productId = $(this).data('product-id');
        const newStock = $(this).val();
        
        $.ajax({
            url: '/admin-dashboard/ajax/update-stock/',
            type: 'POST',
            data: {
                product_id: productId,
                stock: newStock,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    showNotification('Stock updated successfully', 'success');
                }
            }
        });
    });

    // Theme switcher (light/dark mode)
    const currentTheme = localStorage.getItem('theme') || 'light';
    if (currentTheme === 'dark') {
        enableDarkMode();
    }

    $('.theme-switcher').on('click', function() {
        if ($('body').hasClass('dark-mode')) {
            disableDarkMode();
        } else {
            enableDarkMode();
        }
    });

    function enableDarkMode() {
        $('body').addClass('dark-mode');
        localStorage.setItem('theme', 'dark');
    }

    function disableDarkMode() {
        $('body').removeClass('dark-mode');
        localStorage.setItem('theme', 'light');
    }

    // Print functionality
    $('.print-btn').on('click', function() {
        window.print();
    });

    // Export functionality
    $('.export-btn').on('click', function() {
        const format = $(this).data('format');
        const tableId = $(this).data('table');
        
        if (format === 'csv') {
            exportToCSV(tableId);
        } else if (format === 'excel') {
            exportToExcel(tableId);
        } else if (format === 'pdf') {
            exportToPDF(tableId);
        }
    });

    function exportToCSV(tableId) {
        // Implement CSV export logic
        console.log('Exporting to CSV:', tableId);
    }

    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        $('html, body').animate({
            scrollTop: $($(this).attr('href')).offset().top - 80
        }, 500);
    });

    // Auto-logout warning
    let inactivityTime = function() {
        let time;
        window.onload = resetTimer;
        document.onmousemove = resetTimer;
        document.onkeypress = resetTimer;
        
        function logout() {
            showNotification('You will be logged out due to inactivity in 1 minute', 'warning');
            setTimeout(() => {
                window.location.href = '/admin-dashboard/profile/logout/';
            }, 60000);
        }
        
        function resetTimer() {
            clearTimeout(time);
            time = setTimeout(logout, 29 * 60 * 1000); // 29 minutes
        }
    };
    
    inactivityTime();
});

// Global functions
function showKeyboardShortcuts() {
    const shortcuts = `
        <div class="text-start">
            <p><kbd>Ctrl + S</kbd> - Save current form</p>
            <p><kbd>Ctrl + D</kbd> - Go to Dashboard</p>
            <p><kbd>Ctrl + /</kbd> - Show this help</p>
            <p><kbd>Ctrl + F</kbd> - Focus search</p>
            <p><kbd>Ctrl + N</kbd> - Create new item</p>
        </div>
    `;
    
    Swal.fire({
        title: 'Keyboard Shortcuts',
        html: shortcuts,
        icon: 'info',
        confirmButtonText: 'Got it!'
    });
}

function formatCurrency(amount) {
    return '৳' + parseFloat(amount).toLocaleString('en-BD', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-BD', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Dark mode styles
body.dark-mode {
    background-color: #1a1a1a;
    color: #ffffff;
}

body.dark-mode .card {
    background-color: #2d2d2d;
    border-color: #404040;
}

body.dark-mode .table {
    color: #ffffff;
}

body.dark-mode .form-control {
    background-color: #2d2d2d;
    border-color: #404040;
    color: #ffffff;
}

// CSS for pulse animation
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.pulse {
    animation: pulse 0.5s ease-in-out;
}