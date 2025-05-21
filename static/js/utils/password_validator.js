'use strict';
class PasswordValidator {
    constructor(password1Id = 'id_password1', password2Id = 'id_password2') {
        this.password1 = document.getElementById(password1Id);
        this.password2 = document.getElementById(password2Id);
        
        if (!this.password1 || !this.password2) {
            console.error('Password input fields not found');
            return;
        }
        
        // Create error message element for password1
        this.errorMessage = document.createElement('label');
        this.errorMessage.className = 'label';
        this.errorMessage.innerHTML = '<span class="label-text-alt text-error">Passwords do not match</span>';
        this.password1.parentNode.appendChild(this.errorMessage);
        this.errorMessage.style.display = 'none';
        
        // Add event listeners to both password fields
        this.password2.addEventListener('input', () => this.validateMatch());
    }

    validateMatch() {
        const password1Value = this.password1.value;
        const password2Value = this.password2.value;
        
        if (password2Value === '') {
            this.errorMessage.style.display = 'none';
            return;
        }

        if (password1Value !== password2Value) {
            this.password2.classList.add('input-error');
            this.errorMessage.style.display = 'block';
            return false;
        } else {
            this.password2.classList.remove('input-error');
            this.errorMessage.style.display = 'none';
            return true;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new PasswordValidator();
});