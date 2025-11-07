(function () {
    try {
        var root = document.documentElement;
        var LIGHT = 'light-theme';
        var DARK = 'dark-theme';
        var t = null;
        try { t = localStorage.getItem('theme'); } catch (e) { /* ignore */ }
        if (t !== LIGHT && t !== DARK) {
            var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            t = prefersDark ? DARK : LIGHT;
        }
        var isDark = t === DARK;
        root.classList.toggle(DARK, isDark);
        root.classList.toggle(LIGHT, !isDark);
        root.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
    } catch (e) { /* no-op */ }
})();
