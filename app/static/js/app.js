// ========================================
// GASTARI - App JavaScript
// ========================================

// --- Global helpers (needed by inline handlers and templates) ---

function toggleFilterPanel() {
    var panel = document.getElementById('filterPanel');
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
}

function isDarkMode() {
    var theme = document.documentElement.getAttribute('data-theme');
    if (theme === 'system') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return theme === 'dark';
}

function chartBg(alpha) {
    return isDarkMode() ? 'rgba(255,255,255,' + alpha + ')' : 'rgba(0,0,0,' + alpha + ')';
}
function chartLine() {
    return isDarkMode() ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.7)';
}
function chartLineSubtle() {
    return isDarkMode() ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)';
}
function chartGrid() {
    return isDarkMode() ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)';
}
function chartCardBg() {
    return isDarkMode() ? '#1c1c1e' : '#ffffff';
}
function chartText() {
    return isDarkMode() ? '#98989d' : '#6e6e73';
}

// --- Bottom Sheet (Mobile More Menu) ---
function toggleMoreMenu() {
    var overlay = document.getElementById('bottomSheetOverlay');
    var sheet = document.getElementById('bottomSheet');
    if (sheet.classList.contains('show')) {
        closeBottomSheet();
    } else {
        overlay.classList.add('show');
        sheet.classList.add('show');
    }
}

function closeBottomSheet() {
    var overlay = document.getElementById('bottomSheetOverlay');
    var sheet = document.getElementById('bottomSheet');
    overlay.classList.remove('show');
    sheet.classList.remove('show');
}

// --- Theme Management ---
function getStoredTheme() {
    return localStorage.getItem('gastari-theme') || document.documentElement.getAttribute('data-theme') || 'light';
}

function setTheme(theme) {
    localStorage.setItem('gastari-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
}

function applyTheme(theme) {
    if (theme === 'system') {
        var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }
}

// ========================================
// DOM-ready initialisation
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // --- Sidebar toggle (desktop) ---
    var sidebar = document.getElementById('sidebar');
    var toggle = document.getElementById('sidebarToggle');
    var main = document.getElementById('mainContent');

    if (toggle && sidebar) {
        toggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
        if (main) {
            main.addEventListener('click', function() {
                if (sidebar.classList.contains('open')) {
                    sidebar.classList.remove('open');
                }
            });
        }
    }

    // --- Auto-dismiss toasts ---
    document.querySelectorAll('.toast-container .toast').forEach(function(toast) {
        setTimeout(function() {
            toast.classList.add('toast-removing');
            setTimeout(function() { toast.remove(); }, 250);
        }, 4500);
    });

    // --- Theme ---
    applyTheme(getStoredTheme());

    // --- Theme radio buttons ---
    document.querySelectorAll('.theme-option').forEach(function(option) {
        option.addEventListener('click', function() {
            document.querySelectorAll('.theme-option').forEach(function(o) {
                o.classList.remove('selected');
            });
            this.classList.add('selected');
            var input = this.querySelector('input[type="radio"]');
            if (input) input.checked = true;
        });
    });

    // --- Close FAB on outside click ---
    document.addEventListener('click', function(e) {
        var fabContainer = document.querySelector('.fab-container:not(#mobileFabMenu)');
        if (fabContainer && !fabContainer.contains(e.target)) {
            var menu = document.getElementById('fabMenu');
            var fab = document.getElementById('fabMain');
            if (menu) menu.classList.remove('show');
            if (fab) fab.style.transform = '';
        }
    });

    // --- Format money inputs ---
    document.querySelectorAll('input[type="number"]').forEach(function(input) {
        if (input.getAttribute('step') === '0.01') {
            input.addEventListener('blur', function() {
                if (this.value && !isNaN(this.value)) {
                    this.value = parseFloat(this.value).toFixed(2);
                }
            });
        }
    });
});

// --- System theme listener ---
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function() {
    var stored = getStoredTheme();
    if (stored === 'system') {
        applyTheme('system');
    }
});
