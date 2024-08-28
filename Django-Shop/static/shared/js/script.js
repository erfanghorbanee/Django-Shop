// Change the theme of the website
document.getElementById('themeToggle').addEventListener('click', function () {
    document.body.classList.toggle('dark-theme');
    document.body.classList.toggle('light-theme');
    
    // Update icon
    const themeIcon = document.getElementById('themeIcon');
    if (document.body.classList.contains('dark-theme')) {
        themeIcon.classList.remove('bi-brightness-high');
        themeIcon.classList.add('bi-moon');
    } else {
        themeIcon.classList.remove('bi-moon');
        themeIcon.classList.add('bi-brightness-high');
    }
});
