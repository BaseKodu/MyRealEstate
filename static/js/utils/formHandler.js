export function initializeAjaxForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        fetch(window.location.href, {
            method: 'POST',
            body: new FormData(this),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            const toastContainer = document.getElementById('toast-container');
            const toast = document.createElement('div');
            
            if (data.status === 'success') {
                toast.className = 'alert alert-success';
                toast.textContent = data.message;
            } else {
                toast.className = 'alert alert-error';
                // Clear previous error states
                form.querySelectorAll('.input-error').forEach(el => {
                    el.classList.remove('input-error');
                });
                form.querySelectorAll('.error-message').forEach(el => {
                    el.remove();
                });
                
                // Add new error states
                Object.entries(data.errors).forEach(([field, error]) => {
                    const input = form.querySelector(`[name="${field}"]`);
                    if (input) {
                        input.classList.add('input-error');
                        const errorDiv = document.createElement('div');
                        errorDiv.className = 'error-message text-error text-sm mt-1';
                        errorDiv.textContent = error;
                        input.parentNode.appendChild(errorDiv);
                    }
                });
                
                toast.textContent = 'Please correct the errors below';
            }
            
            toastContainer.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        })
        .catch(error => {
            console.error('Error:', error);
            const toastContainer = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'alert alert-error';
            toast.textContent = 'An error occurred. Please try again.';
            toastContainer.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        });
    });
}