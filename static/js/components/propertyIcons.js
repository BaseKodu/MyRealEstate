import * as LucideModule from '../lib/lucide.js';

// Make sure we have the icons object
const LucideIcons = LucideModule.icons || LucideModule;

export class PropertyIcon extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        const iconName = this.getAttribute('name') || 'HelpCircle';
        const size = this.getAttribute('size') || '20';
        const color = this.getAttribute('color') || 'currentColor';
        const strokeWidth = this.getAttribute('stroke-width') || '2';
        
        // Get the icon creation function from Lucide
        const createIcon = LucideIcons[iconName];
        
        if (typeof createIcon === 'function') {
            // Create the SVG element
            const svgElement = createIcon({
                color: color,
                size: size,
                strokeWidth: strokeWidth,
            });
            
            // Add the SVG to the shadow DOM
            this.shadowRoot.innerHTML = svgElement;
        } else {
            console.warn(`Icon "${iconName}" not found in Lucide, using fallback`);
            
            // Fallback to a simple SVG if icon not found
            const fallbackSvg = `
                <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" 
                     stroke="${color}" stroke-width="${strokeWidth}" stroke-linecap="round" 
                     stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
            `;
            
            this.shadowRoot.innerHTML = fallbackSvg;
        }
    }
}

// Define the custom element
if (!customElements.get('property-icon')) {
    customElements.define('property-icon', PropertyIcon);
}

// Export a function to create icons programmatically
export function createIcon(name, options = {}) {
    const iconFn = LucideIcons[name];
    if (typeof iconFn === 'function') {
        return iconFn(options);
    }
    
    // Fallback
    return `<svg width="${options.size || 24}" height="${options.size || 24}" viewBox="0 0 24 24" fill="none" 
                 stroke="${options.color || 'currentColor'}" stroke-width="${options.strokeWidth || 2}" 
                 stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>`;
}