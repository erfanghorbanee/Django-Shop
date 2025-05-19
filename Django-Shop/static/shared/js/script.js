// Theme management
function setTheme(theme) {
    document.body.classList.remove('light-theme', 'dark-theme');
    document.body.classList.add(theme);
    
    // Update icon
    const themeIcon = document.getElementById('themeIcon');
    if (theme === 'dark-theme') {
        themeIcon.classList.remove('bi-brightness-high');
        themeIcon.classList.add('bi-moon');
    } else {
        themeIcon.classList.remove('bi-moon');
        themeIcon.classList.add('bi-brightness-high');
    }
    
    // Save to localStorage
    localStorage.setItem('theme', theme);
}

// Initialize theme from localStorage
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light-theme';
    setTheme(savedTheme);
});

// Theme toggle
document.getElementById('themeToggle').addEventListener('click', function() {
    const currentTheme = document.body.classList.contains('dark-theme') ? 'light-theme' : 'dark-theme';
    setTheme(currentTheme);
});
