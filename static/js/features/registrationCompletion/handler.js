// static/js/features/registrationCompletion.js
import { toaster } from '../components/toaster.js';
import { PasswordValidator } from '../utils/password_validator.js';

export class RegistrationCompletion {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.usernameInput = this.form.querySelector('input[name="username"]');
        
        // Initialize password validator
        this.passwordValidator = new PasswordValidator();
        
        this.init();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.usernameInput.addEventListener('blur', this.checkUsername.bind(this));
    }

    async checkUsername() {
        const username = this.usernameInput.value;
        if (!username) return;

        try {
            const response = await fetch(`/api/users/check-username/?username=${encodeURIComponent(username)}`);
            const data = await response.json();
            
            if (data.exists) {
                this.usernameInput.classList.add('input-error');
                toaster.show('Username is already taken', 'error');
                return false;
            }
            
            this.usernameInput.classList.remove('input-error');
            return true;
        } catch (error) {
            console.error('Error checking username:', error);
            return false;
        }
    }

    async handleSubmit(event) {
        event.preventDefault();

        // Check if passwords match using our existing validator
        const isPasswordValid = this.passwordValidator.validateMatch();
        const isUsernameAvailable = await this.checkUsername();

        if (!isPasswordValid || !isUsernameAvailable) {
            return;
        }

        // If all validations pass, submit the form
        this.form.submit();
    }
}