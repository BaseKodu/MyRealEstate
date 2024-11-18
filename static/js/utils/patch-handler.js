// static/js/patch-handler.js
document.addEventListener('DOMContentLoaded', function() {
    // Listen for all form submissions
    document.addEventListener('submit', async function(e) {
        const form = e.target;
        const formData = new FormData(form);
        
        // Only intercept if it's a PATCH request
        if (formData.get('_method') !== 'PATCH') {
            return; // Let the form submit normally
        }
        
        e.preventDefault();
        
        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                body: formData // Send the FormData directly
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Get the HTML response and update the page
            const html = await response.text();
            document.documentElement.innerHTML = html;
            
            // Re-run any scripts in the new content
            document.querySelectorAll('script').forEach(script => {
                const newScript = document.createElement('script');
                Array.from(script.attributes).forEach(attr => {
                    newScript.setAttribute(attr.name, attr.value);
                });
                newScript.appendChild(document.createTextNode(script.innerHTML));
                script.parentNode.replaceChild(newScript, script);
            });

        } catch (error) {
            alert('Error:', error);
        }
    });
});