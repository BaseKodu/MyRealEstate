import { toaster } from '../../components/toaster.js';

export class ImageUploadHandler {
   constructor(options = {}) {
    this.dropzoneElement = document.getElementById(options.dropzoneId || 'imageUploadForm');
    this.uploadUrl = options.uploadUrl;
    this.deleteUrl = options.deleteUrl || '/properties/images/{id}/delete/';
    this.setPrimaryUrl = options.setPrimaryUrl || '/properties/images/{id}/set-primary/';
    this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    this.maxFiles = options.maxFiles || 50;
    this.maxFileSize = options.maxFileSize || 5; // MB
    this.supportedTypes = options.supportedTypes || ['image/jpeg', 'image/png', 'image/gif'];
       
    this.initializeDropzone();
    this.initializeEventListeners();
   }

   initializeDropzone() {
       this.dropzoneElement.addEventListener('dragover', (e) => {
           e.preventDefault();
           this.dropzoneElement.classList.add('border-primary');
       });

       this.dropzoneElement.addEventListener('dragleave', () => {
           this.dropzoneElement.classList.remove('border-primary');
       });

       this.dropzoneElement.addEventListener('drop', (e) => {
           e.preventDefault();
           this.dropzoneElement.classList.remove('border-primary');
           const files = Array.from(e.dataTransfer.files);
           this.handleFiles(files);
       });

       // Also handle click to select
       const fileInput = document.createElement('input');
       fileInput.type = 'file';
       fileInput.multiple = true;
       fileInput.accept = 'image/*';
       fileInput.classList.add('hidden');
       this.dropzoneElement.appendChild(fileInput);

       this.dropzoneElement.addEventListener('click', () => {
           fileInput.click();
       });

       fileInput.addEventListener('change', (e) => {
           const files = Array.from(e.target.files);
           this.handleFiles(files);
       });
   }

   initializeEventListeners() {
       // Handle delete buttons
       document.addEventListener('click', (e) => {
           if (e.target.matches('.delete-image-btn')) {
               this.handleDelete(e.target.dataset.imageId);
           } else if (e.target.matches('.set-primary-btn')) {
               this.handleSetPrimary(e.target.dataset.imageId);
           }
       });
   }

   async handleFiles(files) {
       const validFiles = files.filter(file => this.validateFile(file));
       
       for (const file of validFiles) {
           try {
               await this.uploadFile(file);
           } catch (error) {
               console.error('Upload failed:', error);
               this.showError(`Failed to upload ${file.name}`);
           }
       }
   }

   validateFile(file) {
       if (!this.supportedTypes.includes(file.type)) {
           this.showError(`${file.name} is not a supported image type`);
           return false;
       }

       if (file.size > this.maxFileSize * 1024 * 1024) {
           this.showError(`${file.name} exceeds maximum file size of ${this.maxFileSize}MB`);
           return false;
       }

       return true;
   }

   async uploadFile(file) {
       const formData = new FormData();
       formData.append('image', file);
       formData.append('image_upload', '1');
       formData.append('csrfmiddlewaretoken', this.csrfToken);

       try {
           const response = await fetch(this.uploadUrl, {
               method: 'POST',
               body: formData,
               headers: {
                   'X-CSRFToken': this.csrfToken,
               }
           });

           if (!response.ok) {
               throw new Error(`HTTP error! status: ${response.status}`);
           }

           const data = await response.json();
           if (data.status === 'success') {
               this.addImageToCarousel(data);
               this.showSuccess(`Image uploaded successfully`);
           } else {
               throw new Error(data.message || 'Upload failed');
           }
       } catch (error) {
           this.showError(`Failed to upload ${file.name}: ${error.message}`);
           throw error;
       }
   }

   addImageToCarousel(imageData) {
       const carousel = document.querySelector('.carousel');
       const template = `
           <div class="carousel-item relative group">
               <img src="${imageData.url}" 
                    alt="${imageData.caption}"
                    class="w-48 h-48 object-cover rounded-lg">
               <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center space-x-2 rounded-lg">
                   <button type="button" 
                           class="btn btn-sm btn-outline btn-primary set-primary-btn"
                           data-image-id="${imageData.image_id}">
                       Set Primary
                   </button>
                   <button type="button" 
                           class="btn btn-sm btn-outline btn-error delete-image-btn"
                           data-image-id="${imageData.image_id}">
                       Delete
                   </button>
               </div>
           </div>
       `;
       carousel.insertAdjacentHTML('beforeend', template);
   }

   async handleDelete(imageId) {
        if (!confirm('Are you sure you want to delete this image?')) return;

        try {
            const url = this.deleteUrl.replace('{id}', imageId);
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                }
            });

            if (response.ok) {
                const item = document.querySelector(`[data-image-id="${imageId}"]`).closest('.carousel-item');
                item.remove();
                this.showSuccess('Image deleted successfully');
            } else {
                throw new Error('Failed to delete image');
            }
        } catch (error) {
            this.showError('Failed to delete image');
            }
    }   

    async handleSetPrimary(imageId) {
        try {
            const url = this.setPrimaryUrl.replace('{id}', imageId);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                }
            });

            if (response.ok) {
                this.showSuccess('Primary image set successfully');
                location.reload();
            } else {
                throw new Error('Failed to set primary image');
            }
        } catch (error) {
            this.showError('Failed to set primary image');
        }
    }

   showError(message) {
       toaster.show(message, 'error');
   }

   showSuccess(message) {
       toaster.show(message, 'success');
   }
}