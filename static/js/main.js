// Main JavaScript functionality for the College Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Attendance marking functionality
    initializeAttendanceMarking();
    
    // File upload enhancements
    initializeFileUploads();
    
    // Form validation enhancements
    initializeFormValidation();
    
    // Data tables
    initializeDataTables();
    
    // Sidebar toggle for mobile
    initializeSidebarToggle();
});

// Attendance marking functionality
function initializeAttendanceMarking() {
    const attendanceForm = document.getElementById('attendanceForm');
    if (attendanceForm) {
        const studentCheckboxes = document.querySelectorAll('input[name^="student_"]');
        const markAllPresent = document.getElementById('markAllPresent');
        const markAllAbsent = document.getElementById('markAllAbsent');
        
        if (markAllPresent) {
            markAllPresent.addEventListener('click', function() {
                studentCheckboxes.forEach(function(checkbox) {
                    const studentRow = checkbox.closest('tr');
                    const presentRadio = studentRow.querySelector('input[value="present"]');
                    if (presentRadio) presentRadio.checked = true;
                });
            });
        }
        
        if (markAllAbsent) {
            markAllAbsent.addEventListener('click', function() {
                studentCheckboxes.forEach(function(checkbox) {
                    const studentRow = checkbox.closest('tr');
                    const absentRadio = studentRow.querySelector('input[value="absent"]');
                    if (absentRadio) absentRadio.checked = true;
                });
            });
        }
        
        // Handle form submission
        attendanceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const studentAttendances = {};
            const rows = document.querySelectorAll('#attendanceTable tbody tr');
            
            rows.forEach(function(row) {
                const studentId = row.dataset.studentId;
                const checkedRadio = row.querySelector('input[type="radio"]:checked');
                if (checkedRadio) {
                    studentAttendances[studentId] = checkedRadio.value;
                }
            });
            
            // Set the hidden field value
            const hiddenField = document.getElementById('student_attendances');
            if (hiddenField) {
                hiddenField.value = JSON.stringify(studentAttendances);
            }
            
            // Submit the form
            attendanceForm.submit();
        });
    }
}

// File upload enhancements
function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        const container = input.closest('.file-upload-container');
        if (!container) return;
        
        // Create drag and drop area
        const dropArea = document.createElement('div');
        dropArea.className = 'file-upload-area';
        dropArea.innerHTML = `
            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
            <p class="mb-0">Drag and drop files here or <strong>click to browse</strong></p>
            <small class="text-muted">Supported formats: JPG, PNG, PDF, DOC, DOCX</small>
        `;
        
        // Insert drop area before the input
        input.parentNode.insertBefore(dropArea, input);
        input.style.display = 'none';
        
        // Handle click on drop area
        dropArea.addEventListener('click', function() {
            input.click();
        });
        
        // Handle drag and drop
        dropArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropArea.classList.add('dragover');
        });
        
        dropArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dropArea.classList.remove('dragover');
        });
        
        dropArea.addEventListener('drop', function(e) {
            e.preventDefault();
            dropArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                updateFileDisplay(dropArea, files[0]);
            }
        });
        
        // Handle file selection
        input.addEventListener('change', function() {
            if (input.files.length > 0) {
                updateFileDisplay(dropArea, input.files[0]);
            }
        });
    });
}

function updateFileDisplay(dropArea, file) {
    const fileName = file.name;
    const fileSize = formatFileSize(file.size);
    
    dropArea.innerHTML = `
        <i class="fas fa-file fa-2x text-success mb-2"></i>
        <p class="mb-0"><strong>${fileName}</strong></p>
        <small class="text-muted">${fileSize}</small>
        <br>
        <small class="text-success">Click to change file</small>
    `;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Form validation enhancements
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (input.checkValidity()) {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            } else {
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
            }
        });
    });
}

// Data tables initialization
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(function(table) {
        // Add search functionality
        addTableSearch(table);
        
        // Add sorting functionality
        addTableSorting(table);
        
        // Add pagination if needed
        if (table.rows.length > 20) {
            addTablePagination(table);
        }
    });
}

function addTableSearch(table) {
    const searchContainer = document.createElement('div');
    searchContainer.className = 'mb-3';
    searchContainer.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <input type="text" class="form-control" placeholder="Search..." id="tableSearch_${table.id}">
            </div>
        </div>
    `;
    
    table.parentNode.insertBefore(searchContainer, table);
    
    const searchInput = searchContainer.querySelector('input');
    searchInput.addEventListener('keyup', function() {
        const filter = searchInput.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(function(row) {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });
}

function addTableSorting(table) {
    const headers = table.querySelectorAll('thead th');
    
    headers.forEach(function(header, index) {
        if (header.classList.contains('sortable')) {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';
            
            header.addEventListener('click', function() {
                sortTable(table, index);
            });
        }
    });
}

function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAscending = table.dataset.sortDirection !== 'asc';
    
    rows.sort(function(a, b) {
        const aText = a.cells[column].textContent.trim();
        const bText = b.cells[column].textContent.trim();
        
        if (isAscending) {
            return aText.localeCompare(bText, undefined, { numeric: true });
        } else {
            return bText.localeCompare(aText, undefined, { numeric: true });
        }
    });
    
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    
    table.dataset.sortDirection = isAscending ? 'asc' : 'desc';
    
    // Update sort icons
    const headers = table.querySelectorAll('thead th');
    headers.forEach(function(header) {
        const icon = header.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-sort text-muted';
        }
    });
    
    const currentHeader = headers[column];
    const currentIcon = currentHeader.querySelector('i');
    if (currentIcon) {
        currentIcon.className = isAscending ? 'fas fa-sort-up text-primary' : 'fas fa-sort-down text-primary';
    }
}

// Sidebar toggle for mobile
function initializeSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
}

// Utility functions
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner"></span> Loading...';
    button.disabled = true;
    button.dataset.originalText = originalText;
}

function hideLoading(button) {
    const originalText = button.dataset.originalText;
    if (originalText) {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(toast);
        bsAlert.close();
    }, 5000);
}

// Course and date selection for attendance
function loadAttendanceView() {
    const courseSelect = document.getElementById('course_id');
    const dateInput = document.getElementById('date');
    
    if (courseSelect && dateInput) {
        function updateAttendanceView() {
            const courseId = courseSelect.value;
            const date = dateInput.value;
            
            if (courseId && date) {
                const url = new URL(window.location.href);
                url.searchParams.set('course_id', courseId);
                url.searchParams.set('date', date);
                window.location.href = url.toString();
            }
        }
        
        courseSelect.addEventListener('change', updateAttendanceView);
        dateInput.addEventListener('change', updateAttendanceView);
    }
}

// Initialize course/date selection
document.addEventListener('DOMContentLoaded', loadAttendanceView);

// Mobile Navigation Functions
function toggleMobileMenu() {
    const nav = document.getElementById('mainNav');
    const toggle = document.querySelector('.mobile-menu-toggle');
    
    if (nav) {
        nav.classList.toggle('mobile-active');
        nav.classList.toggle('mobile-hidden');
        
        // Update toggle icon
        const icon = toggle.querySelector('i');
        if (nav.classList.contains('mobile-active')) {
            icon.className = 'fas fa-times';
        } else {
            icon.className = 'fas fa-bars';
        }
    }
}

function toggleMobileDropdown(dropdownElement) {
    if (window.innerWidth <= 768) {
        dropdownElement.classList.toggle('mobile-expanded');
    }
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(e) {
    const nav = document.getElementById('mainNav');
    const toggle = document.querySelector('.mobile-menu-toggle');
    
    if (nav && toggle && window.innerWidth <= 768) {
        if (!nav.contains(e.target) && !toggle.contains(e.target)) {
            nav.classList.add('mobile-hidden');
            nav.classList.remove('mobile-active');
            
            const icon = toggle.querySelector('i');
            icon.className = 'fas fa-bars';
        }
    }
});

// Handle window resize
window.addEventListener('resize', function() {
    const nav = document.getElementById('mainNav');
    const toggle = document.querySelector('.mobile-menu-toggle');
    
    if (nav && toggle) {
        if (window.innerWidth > 768) {
            nav.classList.remove('mobile-hidden', 'mobile-active');
            const icon = toggle.querySelector('i');
            icon.className = 'fas fa-bars';
        } else {
            nav.classList.add('mobile-hidden');
        }
    }
});

// Export functions for global access
window.CollegeManagement = {
    showLoading,
    hideLoading,
    confirmDelete,
    showToast,
    formatFileSize
};

// Export mobile functions globally
window.toggleMobileMenu = toggleMobileMenu;
window.toggleMobileDropdown = toggleMobileDropdown;
