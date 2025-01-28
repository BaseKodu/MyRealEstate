import { toaster } from '../../components/toaster';

export class UserInvitationModal {
    constructor() {
        this.modalToggle = document.getElementById('invite-user-modal');
        this.form = document.getElementById('invite-user-form');
        this.emailInput = this.form.querySelector('input[name="email"]');
        
        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    closeModal() {
        this.modalToggle.checked = false;
        this.form.reset();
    }

    async handleSubmit(event) {
        event.preventDefault();
        const formData = new FormData(this.form);

        try {
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            const data = await response.json();

            if (response.ok) {
                toaster.show('Invitation sent successfully!', 'success');
                this.closeModal();
                // Reload the page to update the user list
                window.location.reload();
            } else {
                toaster.show(data.error || 'Error sending invitation', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            toaster.show('An unexpected error occurred', 'error');
        }
    }
}