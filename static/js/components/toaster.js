export class Toaster {
    constructor() {
        // Check if container already exists
        this.container = document.getElementById('toast-container') || this.createContainer();
    }
    
    createContainer() {
        const container = document.createElement('div');
        container.setAttribute('id', 'toast-container');
        container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2';
        document.body.appendChild(container);
        return container;
    }
    
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        
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
        
        const typeClass = `alert-${type}`;
        
        toast.className = [...baseClasses, typeClass].join(' ');
        
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
        
        requestAnimationFrame(() => {
            toast.classList.remove('opacity-0', 'translate-x-full');
        });
        
        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-x-full');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// Create and export a singleton instance
const toaster = new Toaster();
export { toaster }; 