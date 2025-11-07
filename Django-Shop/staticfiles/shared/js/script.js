// Theme management
(function () {
    'use strict';

    const root = document.documentElement; // apply classes on <html>
    const STORAGE_KEY = 'theme';
    const LIGHT = 'light-theme';
    const DARK = 'dark-theme';

    function getSavedTheme() {
        try {
            const t = localStorage.getItem(STORAGE_KEY);
            return t === DARK || t === LIGHT ? t : null;
        } catch (_) {
            return null;
        }
    }

    function getInitialTheme() {
        const saved = getSavedTheme();
        if (saved) return saved;
        if (root.classList.contains(DARK)) return DARK;
        if (root.classList.contains(LIGHT)) return LIGHT;
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        return prefersDark ? DARK : LIGHT;
    }

    function applyTheme(theme, persist) {
        const isDark = theme === DARK;
        root.classList.toggle(DARK, isDark);
        root.classList.toggle(LIGHT, !isDark);
        // Sync Bootstrap color mode for consistency
        root.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');

        const icon = document.getElementById('themeIcon');
        if (icon) {
            icon.classList.toggle('bi-moon', isDark);
            icon.classList.toggle('bi-brightness-high', !isDark);
        }

        if (persist) {
            try { localStorage.setItem(STORAGE_KEY, theme); } catch (_) { /* ignore */ }
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        applyTheme(getInitialTheme(), false);

        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', function () {
                const next = root.classList.contains(DARK) ? LIGHT : DARK;
                applyTheme(next, true);
            });
        }
    });
})();
