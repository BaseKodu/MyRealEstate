document.addEventListener('DOMContentLoaded', function() {
    const deleteModal = document.getElementById('delete-modal');
    const deleteModalContent = document.getElementById('delete-modal-content');

    // Handle delete button clicks
    document.addEventListener('click', async function(e) {
        if (!e.target.classList.contains('delete-btn')) return;
        
        e.preventDefault();
        const url = e.target.dataset.url;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            if (response.ok) {
                deleteModalContent.innerHTML = data.html;
                deleteModal.showModal();
            } else {
                console.error('Error fetching delete modal:', data.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Handle delete form submission
    document.addEventListener('submit', async function(e) {
        if (!e.target.classList.contains('delete-form')) return;
        
        e.preventDefault();
        const form = e.target;
        
        try {
            const response = await fetch(form.action, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Show success message (if you have a toast/notification system)
                if (data.message) {
                    console.log
                }
                
                // Close the modal
                deleteModal.close();
                
                // Remove the row from the table or redirect
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    const row = form.closest('tr');
                    if (row) row.remove();
                }
            } else {
                // Show error message
                
            }
        } catch (error) {
            console.error('An Unecpected error occured: ', error);
        }
    });
});