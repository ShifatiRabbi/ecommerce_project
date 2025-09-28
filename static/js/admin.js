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

// ===== NEW ENHANCEMENTS =====

// Advanced Order Management
function initOrderManagement() {
    // Real-time order updates
    const orderSocket = new WebSocket('ws://localhost:8000/ws/orders/');
    
    orderSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'new_order') {
            showNotification(`New order received: #${data.order_number}`, 'success');
            updateOrderStats();
        } else if (data.type === 'status_update') {
            updateOrderStatus(data.order_id, data.new_status);
        }
    };
    
    orderSocket.onclose = function(e) {
        console.log('Order WebSocket disconnected');
        setTimeout(initOrderManagement, 5000); // Reconnect after 5 seconds
    };
}

// Advanced Search with Filters
function initAdvancedSearch() {
    const searchInput = $('#global-search');
    const searchResults = $('#search-results');
    
    let searchTimeout;
    
    searchInput.on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val();
        
        if (query.length > 2) {
            searchTimeout = setTimeout(() => {
                performGlobalSearch(query);
            }, 500);
        } else {
            searchResults.hide();
        }
    });
    
    function performGlobalSearch(query) {
        $.ajax({
            url: '/admin-dashboard/ajax/global-search/',
            type: 'GET',
            data: { q: query },
            success: function(response) {
                displaySearchResults(response);
            }
        });
    }
    
    function displaySearchResults(results) {
        let html = '';
        
        if (results.products.length > 0) {
            html += '<div class="search-category"><strong>Products</strong></div>';
            results.products.forEach(product => {
                html += `
                    <a href="/admin-dashboard/products/edit/${product.id}/" class="search-item">
                        <i class="fas fa-cube me-2"></i>
                        ${product.name}
                        <span class="text-muted">${product.sku}</span>
                    </a>
                `;
            });
        }
        
        if (results.orders.length > 0) {
            html += '<div class="search-category"><strong>Orders</strong></div>';
            results.orders.forEach(order => {
                html += `
                    <a href="/admin-dashboard/orders/${order.id}/" class="search-item">
                        <i class="fas fa-shopping-cart me-2"></i>
                        Order #${order.order_number}
                        <span class="text-muted">${order.customer_name}</span>
                    </a>
                `;
            });
        }
        
        if (results.customers.length > 0) {
            html += '<div class="search-category"><strong>Customers</strong></div>';
            results.customers.forEach(customer => {
                html += `
                    <a href="/admin-dashboard/customers/${customer.id}/" class="search-item">
                        <i class="fas fa-user me-2"></i>
                        ${customer.name}
                        <span class="text-muted">${customer.email}</span>
                    </a>
                `;
            });
        }
        
        if (html === '') {
            html = '<div class="search-item text-muted">No results found</div>';
        }
        
        searchResults.html(html).show();
    }
}

// Bulk Image Processing
function initBulkImageProcessor() {
    const dropzone = $('#bulk-image-upload');
    const progressBar = $('#upload-progress');
    const fileList = $('#file-list');
    
    dropzone.on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('dragover');
    });
    
    dropzone.on('dragleave', function() {
        $(this).removeClass('dragover');
    });
    
    dropzone.on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
        const files = e.originalEvent.dataTransfer.files;
        processFiles(files);
    });
    
    $('#image-files').on('change', function(e) {
        processFiles(e.target.files);
    });
    
    function processFiles(files) {
        const formData = new FormData();
        
        for (let file of files) {
            if (file.type.startsWith('image/')) {
                formData.append('images', file);
                addFileToList(file);
            }
        }
        
        if (formData.has('images')) {
            uploadFiles(formData);
        }
    }
    
    function addFileToList(file) {
        const fileItem = $(`
            <div class="file-item" data-filename="${file.name}">
                <div class="file-info">
                    <i class="fas fa-image me-2"></i>
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">(${formatFileSize(file.size)})</span>
                </div>
                <div class="file-status">
                    <span class="status-text">Pending</span>
                    <div class="progress" style="height: 4px; width: 100px;">
                        <div class="progress-bar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        `);
        
        fileList.append(fileItem);
    }
    
    function uploadFiles(formData) {
        $.ajax({
            url: '/admin-dashboard/ajax/bulk-image-upload/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            xhr: function() {
                const xhr = new XMLHttpRequest();
                
                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        progressBar.css('width', percentComplete + '%');
                    }
                }, false);
                
                return xhr;
            },
            success: function(response) {
                if (response.success) {
                    showNotification(`${response.uploaded_count} images uploaded successfully!`, 'success');
                    updateFileStatuses(response.results);
                }
            }
        });
    }
    
    function updateFileStatuses(results) {
        results.forEach(result => {
            const fileItem = $(`.file-item[data-filename="${result.filename}"]`);
            const statusText = fileItem.find('.status-text');
            const progressBar = fileItem.find('.progress-bar');
            
            if (result.success) {
                statusText.text('Uploaded').addClass('text-success');
                progressBar.css('width', '100%').addClass('bg-success');
            } else {
                statusText.text('Failed').addClass('text-danger');
                progressBar.css('width', '100%').addClass('bg-danger');
            }
        });
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Advanced Data Export
function initDataExporter() {
    $('#export-data').on('click', function() {
        const modal = $('#exportModal');
        modal.modal('show');
    });
    
    $('#export-form').on('submit', function(e) {
        e.preventDefault();
        const formData = $(this).serialize();
        
        $.ajax({
            url: '/admin-dashboard/ajax/export-data/',
            type: 'POST',
            data: formData,
            xhr: function() {
                const xhr = new XMLHttpRequest();
                xhr.responseType = 'blob';
                return xhr;
            },
            success: function(data, status, xhr) {
                const blob = new Blob([data]);
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                // Get filename from response headers
                const contentDisposition = xhr.getResponseHeader('Content-Disposition');
                let filename = 'export.csv';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                    if (filenameMatch.length === 2) {
                        filename = filenameMatch[1];
                    }
                }
                
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                showNotification('Export completed successfully!', 'success');
                $('#exportModal').modal('hide');
            }
        });
    });
}

// Real-time Dashboard Updates
function initRealTimeDashboard() {
    // Update stats every 30 seconds
    setInterval(updateDashboardStats, 30000);
    
    // Initialize charts with real-time data
    initRealTimeCharts();
}

function initRealTimeCharts() {
    const salesChart = Chart.getChart('salesChart');
    const ordersChart = Chart.getChart('ordersChart');
    
    setInterval(() => {
        $.ajax({
            url: '/admin-dashboard/ajax/real-time-stats/',
            type: 'GET',
            success: function(data) {
                // Update sales chart
                if (salesChart) {
                    salesChart.data.datasets[0].data = data.sales_data;
                    salesChart.update('none');
                }
                
                // Update orders chart
                if (ordersChart) {
                    ordersChart.data.datasets[0].data = data.orders_data;
                    ordersChart.update('none');
                }
            }
        });
    }, 60000); // Update every minute
}

// Advanced Form Validation
function initAdvancedValidation() {
    $.validator.addMethod("phoneBD", function(value, element) {
        return this.optional(element) || /^(?:\+88|01)?\d{11}$/.test(value);
    }, "Please enter a valid Bangladeshi phone number");
    
    $.validator.addMethod("slug", function(value, element) {
        return this.optional(element) || /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value);
    }, "Please enter a valid slug (lowercase letters, numbers, and hyphens)");
    
    // Initialize validation on all forms
    $('form').each(function() {
        $(this).validate({
            errorClass: "is-invalid",
            validClass: "is-valid",
            errorElement: "div",
            errorPlacement: function(error, element) {
                error.addClass("invalid-feedback");
                element.after(error);
            },
            highlight: function(element, errorClass, validClass) {
                $(element).addClass(errorClass).removeClass(validClass);
            },
            unhighlight: function(element, errorClass, validClass) {
                $(element).removeClass(errorClass).addClass(validClass);
            }
        });
    });
}

// Performance Monitoring
function initPerformanceMonitor() {
    let lastLoadTime = Date.now();
    
    $(document).ajaxStart(function() {
        lastLoadTime = Date.now();
        $('body').addClass('loading');
    });
    
    $(document).ajaxStop(function() {
        const loadTime = Date.now() - lastLoadTime;
        $('body').removeClass('loading');
        
        // Log slow requests
        if (loadTime > 5000) {
            console.warn(`Slow request detected: ${loadTime}ms`);
        }
    });
    
    // Monitor page load performance
    window.addEventListener('load', function() {
        const loadTime = Date.now() - performance.timing.navigationStart;
        console.log(`Page loaded in ${loadTime}ms`);
    });
}

// Initialize all enhanced features when document is ready
$(document).ready(function() {
    initOrderManagement();
    initAdvancedSearch();
    initBulkImageProcessor();
    initDataExporter();
    initRealTimeDashboard();
    initAdvancedValidation();
    initPerformanceMonitor();
    
    // Additional initialization
    initTooltips();
    initKeyboardShortcuts();
    initAutoSave();
});

// Enhanced Tooltip System
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover focus',
            delay: { show: 500, hide: 100 }
        });
    });
}

// Enhanced Keyboard Shortcuts
function initKeyboardShortcuts() {
    const shortcuts = {
        'ctrl+shift+p': function() {
            // Quick product add
            window.location.href = '/admin-dashboard/products/add/';
        },
        'ctrl+shift+o': function() {
            // Quick order view
            window.location.href = '/admin-dashboard/orders/';
        },
        'ctrl+shift+s': function() {
            // Quick search focus
            $('#global-search').focus();
        },
        'ctrl+shift+d': function() {
            // Toggle dark mode
            $('body').toggleClass('dark-mode');
            localStorage.setItem('theme', $('body').hasClass('dark-mode') ? 'dark' : 'light');
        }
    };
    
    $(document).on('keydown', function(e) {
        let key = '';
        
        if (e.ctrlKey) key += 'ctrl+';
        if (e.shiftKey) key += 'shift+';
        
        key += e.key.toLowerCase();
        
        if (shortcuts[key]) {
            e.preventDefault();
            shortcuts[key]();
        }
    });
}

// Enhanced Auto-save
function initAutoSave() {
    let autoSaveTimeout;
    let isDirty = false;
    
    $('.auto-save').on('input change', function() {
        isDirty = true;
        clearTimeout(autoSaveTimeout);
        
        autoSaveTimeout = setTimeout(() => {
            if (isDirty) {
                saveFormData();
            }
        }, 2000);
    });
    
    function saveFormData() {
        const form = $('.auto-save').closest('form');
        const formData = new FormData(form[0]);
        
        $.ajax({
            url: form.attr('action') + '?autosave=true',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    showNotification('Changes saved automatically', 'success', 2000);
                    isDirty = false;
                }
            }
        });
    }
    
    // Warn before leaving if there are unsaved changes
    $(window).on('beforeunload', function() {
        if (isDirty) {
            return 'You have unsaved changes. Are you sure you want to leave?';
        }
    });
}

// Utility Functions
function formatCurrency(amount, currency = 'BDT') {
    const formatter = new Intl.NumberFormat('en-BD', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2
    });
    return formatter.format(amount);
}

function formatDate(dateString, format = 'medium') {
    const date = new Date(dateString);
    const options = {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        medium: { year: 'numeric', month: 'long', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
    };
    
    return date.toLocaleDateString('en-BD', options[format] || options.medium);
}

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

// Export utility functions for global use
window.adminUtils = {
    formatCurrency,
    formatDate,
    debounce,
    showNotification: window.showNotification
};