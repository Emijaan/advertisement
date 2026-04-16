// Theme toggle
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
}

// Apply saved theme
(function() {
    const saved = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
})();

// Mobile sidebar toggle
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
}

// Auto-dismiss messages after 4s
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(msg) {
        setTimeout(function() {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100%)';
            setTimeout(function() { msg.remove(); }, 300);
        }, 4000);
    });
});

// Delete confirmation
function confirmDelete(url) {
    if (confirm('Are you sure you want to delete this? This action cannot be undone.')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrf) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = csrf.value;
            form.appendChild(input);
        }
        document.body.appendChild(form);
        form.submit();
    }
}

// Dropdown toggle
function toggleDropdown(el) {
    const menu = el.nextElementSibling;
    document.querySelectorAll('.dropdown-menu.show').forEach(function(m) {
        if (m !== menu) m.classList.remove('show');
    });
    menu.classList.toggle('show');
}

// Close dropdowns on click outside
document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu.show').forEach(function(m) {
            m.classList.remove('show');
        });
    }
});
