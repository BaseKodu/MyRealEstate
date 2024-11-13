'use strict';
class PasswordValidator {
    constructor(password1Id = 'id_password1', password2Id = 'id_password2') {
        this.password1 = document.getElementById(password1Id);
        this.password2 = document.getElementById(password2Id);
        
        if (!this.password1 || !this.password2) {
            console.error('Password input fields not found');
            return;
        }
        
        // Add event listeners to both password fields
        this.password2.addEventListener('input', () => this.validateMatch());
    }

    validateMatch() {
        const password1Value = this.password1.value;
        const password2Value = this.password2.value;
        
        if (password2Value === '') {
            return;
        }

        if (password1Value !== password2Value) {
        window.toaster.show('Passwords do not match', 'error');
            this.password2.classList.add('input-error');
            return false;
        } else {
            this.password2.classList.remove('input-error');
            return true;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PasswordValidator();
});