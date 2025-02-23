document.addEventListener('DOMContentLoaded', function() {
    // Handle manual sync trigger
    const syncButton = document.getElementById('triggerSync');
    if (syncButton) {
        syncButton.addEventListener('click', function() {
            syncButton.disabled = true;
            syncButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Syncing...';

            fetch('/trigger-sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert('success', 'Sync triggered successfully');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showAlert('danger', 'Sync failed: ' + data.message);
                }
            })
            .catch(error => {
                showAlert('danger', 'Error triggering sync: ' + error);
            })
            .finally(() => {
                syncButton.disabled = false;
                syncButton.innerHTML = '<i class="fas fa-sync"></i> Trigger Sync';
            });
        });
    }

    // Handle password visibility toggle
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            const input = document.querySelector(this.getAttribute('data-target'));
            if (input.type === 'password') {
                input.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                input.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
});

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
