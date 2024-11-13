// static/js/components/toaster.js
class Toaster {
    constructor() {
        // Check if container already exists (useful for turbo/htmx)
        this.container = document.getElementById('toast-container') || this.createContainer();
    }
    
    createContainer() {
        const container = document.createElement('div');
        container.setAttribute('id', 'toast-container');
        // Using Tailwind classes that are now safelisted
        container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2';
        document.body.appendChild(container);
        return container;
    }
    
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        
        // Base classes
        const baseClasses = [
            'alert',
            'shadow-lg',
            'transition-all',
            'duration-300',
            'ease-in-out',
            'opacity-0',
            'transform',
            'translate-x-full'
        ];
        
        // Add type-specific class
        const typeClass = `alert-${type}`;
        
        toast.className = [...baseClasses, typeClass].join(' ');
        
        // Use template literal for better readability
        toast.innerHTML = `
            <span>${message}</span>
            <button class="btn btn-circle btn-xs" onclick="this.parentElement.remove()">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" 
                     viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" 
                          stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        `;
        
        this.container.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.classList.remove('opacity-0', 'translate-x-full');
        });
        
        // Auto remove
        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-x-full');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// Create global instance
window.toaster = new Toaster();