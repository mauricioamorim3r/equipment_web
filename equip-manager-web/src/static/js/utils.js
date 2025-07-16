// Utility Functions

// Loading Overlay
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Toast Notifications
function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = getToastIcon(type);
    
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="closeToast(this)">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            closeToast(toast.querySelector('.toast-close'));
        }
    }, duration);
}

function getToastIcon(type) {
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

function closeToast(button) {
    const toast = button.closest('.toast');
    if (toast) {
        toast.style.animation = 'toastSlideOut 0.3s ease forwards';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

// Add CSS for slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes toastSlideOut {
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);

// Date Utilities
function formatDate(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    } catch (error) {
        return dateString;
    }
}

function formatDateTime(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    } catch (error) {
        return dateString;
    }
}

function isValidDate(dateString) {
    if (!dateString) return false;
    const date = new Date(dateString);
    return !isNaN(date.getTime());
}

function getDateDifference(date1, date2) {
    const d1 = new Date(date1);
    const d2 = new Date(date2);
    const diffTime = d2 - d1;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

function getDaysUntil(dateString) {
    if (!dateString) return null;
    
    try {
        const targetDate = new Date(dateString);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        targetDate.setHours(0, 0, 0, 0);
        
        const diffTime = targetDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    } catch (error) {
        return null;
    }
}

// Status Utilities
function getStatusCalibacao(dataProximaCalibacao) {
    if (!dataProximaCalibacao) {
        return { status: 'sem-data', text: 'Sem Data', class: 'sem-data' };
    }

    const dias = getDaysUntil(dataProximaCalibacao);
    
    if (dias === null) {
        return { status: 'data-invalida', text: 'Data Inválida', class: 'sem-data' };
    }
    
    if (dias < 0) {
        return { status: 'vencido', text: 'Vencido', class: 'vencido' };
    } else if (dias <= 30) {
        return { status: 'proximo-vencimento', text: 'Próximo Vencimento', class: 'proximo-vencimento' };
    } else {
        return { status: 'vigente', text: 'Vigente', class: 'vigente' };
    }
}

function createStatusBadge(status) {
    const statusInfo = typeof status === 'string' ? getStatusCalibacao(status) : status;
    return `<span class="status-badge ${statusInfo.class}">${statusInfo.text}</span>`;
}

// Number Utilities
function formatNumber(number, decimals = 2) {
    if (number === null || number === undefined || number === '') return '-';
    
    try {
        return parseFloat(number).toLocaleString('pt-BR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    } catch (error) {
        return number;
    }
}

function formatCurrency(value) {
    if (value === null || value === undefined || value === '') return '-';
    
    try {
        return parseFloat(value).toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });
    } catch (error) {
        return value;
    }
}

// String Utilities
function truncateText(text, maxLength = 50) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function slugify(text) {
    return text
        .toString()
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')
        .replace(/[^\w\-]+/g, '')
        .replace(/\-\-+/g, '-')
        .replace(/^-+/, '')
        .replace(/-+$/, '');
}

// DOM Utilities
function createElement(tag, className = '', innerHTML = '') {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (innerHTML) element.innerHTML = innerHTML;
    return element;
}

function clearElement(element) {
    if (element) {
        element.innerHTML = '';
    }
}

function toggleClass(element, className) {
    if (element) {
        element.classList.toggle(className);
    }
}

function addClass(element, className) {
    if (element) {
        element.classList.add(className);
    }
}

function removeClass(element, className) {
    if (element) {
        element.classList.remove(className);
    }
}

function hasClass(element, className) {
    return element ? element.classList.contains(className) : false;
}

// Form Utilities
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        // Handle checkboxes and multiple values
        if (data[key]) {
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }
    
    return data;
}

function setFormData(form, data) {
    if (!form || !data) return;
    
    Object.keys(data).forEach(key => {
        const element = form.elements[key];
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = Boolean(data[key]);
            } else if (element.type === 'radio') {
                const radioButton = form.querySelector(`input[name="${key}"][value="${data[key]}"]`);
                if (radioButton) radioButton.checked = true;
            } else {
                element.value = data[key] || '';
            }
        }
    });
}

function clearForm(form) {
    if (!form) return;
    
    form.reset();
    
    // Clear any custom validation states
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.classList.remove('error', 'success');
    });
}

function validateForm(form, rules = {}) {
    if (!form) return false;
    
    let isValid = true;
    const errors = {};
    
    Object.keys(rules).forEach(fieldName => {
        const field = form.elements[fieldName];
        const rule = rules[fieldName];
        
        if (!field) return;
        
        // Required validation
        if (rule.required && !field.value.trim()) {
            isValid = false;
            errors[fieldName] = rule.requiredMessage || 'Este campo é obrigatório';
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
        
        // Custom validation
        if (rule.validate && field.value.trim()) {
            const customResult = rule.validate(field.value);
            if (customResult !== true) {
                isValid = false;
                errors[fieldName] = customResult;
                field.classList.add('error');
            }
        }
    });
    
    return { isValid, errors };
}

// Table Utilities
function createTableRow(data, columns) {
    const row = document.createElement('tr');
    
    columns.forEach(column => {
        const cell = document.createElement('td');
        
        if (column.render) {
            cell.innerHTML = column.render(data[column.key], data);
        } else {
            cell.textContent = data[column.key] || '-';
        }
        
        if (column.className) {
            cell.className = column.className;
        }
        
        row.appendChild(cell);
    });
    
    return row;
}

function sortTableData(data, column, direction = 'asc') {
    return [...data].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle null/undefined values
        if (aVal === null || aVal === undefined) aVal = '';
        if (bVal === null || bVal === undefined) bVal = '';
        
        // Convert to string for comparison
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();
        
        if (direction === 'asc') {
            return aVal.localeCompare(bVal);
        } else {
            return bVal.localeCompare(aVal);
        }
    });
}

// Pagination Utilities
function createPagination(container, currentPage, totalPages, onPageChange) {
    if (!container) return;
    
    clearElement(container);
    
    if (totalPages <= 1) return;
    
    const pagination = document.createElement('div');
    pagination.className = 'pagination';
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => onPageChange(currentPage - 1);
    pagination.appendChild(prevBtn);
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        const firstBtn = document.createElement('button');
        firstBtn.textContent = '1';
        firstBtn.onclick = () => onPageChange(1);
        pagination.appendChild(firstBtn);
        
        if (startPage > 2) {
            const dots = document.createElement('span');
            dots.textContent = '...';
            dots.className = 'pagination-dots';
            pagination.appendChild(dots);
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === currentPage ? 'active' : '';
        pageBtn.onclick = () => onPageChange(i);
        pagination.appendChild(pageBtn);
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const dots = document.createElement('span');
            dots.textContent = '...';
            dots.className = 'pagination-dots';
            pagination.appendChild(dots);
        }
        
        const lastBtn = document.createElement('button');
        lastBtn.textContent = totalPages;
        lastBtn.onclick = () => onPageChange(totalPages);
        pagination.appendChild(lastBtn);
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => onPageChange(currentPage + 1);
    pagination.appendChild(nextBtn);
    
    container.appendChild(pagination);
}

// Search and Filter Utilities
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function filterData(data, searchTerm, searchFields) {
    if (!searchTerm) return data;
    
    const term = searchTerm.toLowerCase();
    
    return data.filter(item => {
        return searchFields.some(field => {
            const value = item[field];
            return value && String(value).toLowerCase().includes(term);
        });
    });
}

// Local Storage Utilities
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        return defaultValue;
    }
}

function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Error removing from localStorage:', error);
    }
}

// URL Utilities
function updateURLParams(params) {
    const url = new URL(window.location);
    Object.keys(params).forEach(key => {
        if (params[key]) {
            url.searchParams.set(key, params[key]);
        } else {
            url.searchParams.delete(key);
        }
    });
    window.history.replaceState({}, '', url);
}

function getURLParams() {
    const params = {};
    const urlParams = new URLSearchParams(window.location.search);
    for (const [key, value] of urlParams) {
        params[key] = value;
    }
    return params;
}

// File Utilities
function downloadFile(data, filename, type = 'text/plain') {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = e => reject(e);
        reader.readAsText(file);
    });
}

// Animation Utilities
function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.display = 'block';
    
    const start = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        element.style.opacity = progress;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

function fadeOut(element, duration = 300) {
    const start = performance.now();
    const startOpacity = parseFloat(getComputedStyle(element).opacity);
    
    function animate(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        element.style.opacity = startOpacity * (1 - progress);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            element.style.display = 'none';
        }
    }
    
    requestAnimationFrame(animate);
}

// Error Handling
function handleError(error, context = '') {
    console.error(`Error ${context}:`, error);
    
    let message = 'Ocorreu um erro inesperado';
    
    if (error.message) {
        message = error.message;
    } else if (typeof error === 'string') {
        message = error;
    }
    
    showToast(message, 'error');
}

// Export utilities for use in other modules
window.Utils = {
    showLoading,
    hideLoading,
    showToast,
    closeToast,
    formatDate,
    formatDateTime,
    formatNumber,
    formatCurrency,
    getStatusCalibacao,
    createStatusBadge,
    getDaysUntil,
    truncateText,
    capitalizeFirst,
    createElement,
    clearElement,
    getFormData,
    setFormData,
    clearForm,
    validateForm,
    createTableRow,
    createPagination,
    debounce,
    filterData,
    saveToLocalStorage,
    loadFromLocalStorage,
    handleError,
    downloadFile
};

