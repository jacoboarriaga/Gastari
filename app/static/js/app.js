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

// --- Page loading bar (PWA navigation feedback) ---
(function() {
    var loader = document.getElementById('pageLoader');
    if (!loader) return;

    // Animate loading completion on every page load
    function animateLoad() {
        // Start hidden
        loader.style.width = '0';
        loader.style.opacity = '1';
        // Force reflow
        void loader.offsetWidth;
        // Animate to full
        loader.style.transition = 'width 0.4s cubic-bezier(0.4,0,0.2,1)';
        loader.style.width = '100%';
        // Fade out after completion
        setTimeout(function() {
            loader.style.transition = 'opacity 0.3s ease';
            loader.style.opacity = '0';
        }, 500);
    }

    // Run on first paint
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', animateLoad);
    } else {
        animateLoad();
    }

    // Also on pageshow (for back/forward cache)
    window.addEventListener('pageshow', animateLoad);

    // Show loading bar when clicking internal links
    document.addEventListener('click', function(e) {
        var link = e.target.closest('a');
        if (link) {
            var href = link.getAttribute('href');
            if (href && href.indexOf('#') !== 0 && href.indexOf('javascript:') !== 0 && !link.hasAttribute('download')) {
                loader.style.transition = 'none';
                loader.style.opacity = '1';
                loader.style.width = '20%';
            }
        }
    });

    // Form submission: show loader + disable button
    document.addEventListener('submit', function(e) {
        loader.style.transition = 'none';
        loader.style.opacity = '1';
        loader.style.width = '30%';
        var btn = e.target.querySelector('button[type="submit"], input[type="submit"]');
        if (btn && !btn.classList.contains('btn-loading')) {
            btn.classList.add('btn-loading');
        }
    });
})();

// --- Liquid Glass: specular highlight (todas las plataformas) ---
(function() {
    var glassSelector = '.glass, .section-card, .summary-card, .chart-card, .form-card, .account-card, .modal-card, .bottom-sheet, .toast, .settings-section, .filter-panel, .budget-card, .debt-card, .auth-card';
    var glassEls = document.querySelectorAll(glassSelector);
    glassEls.forEach(function(el) {
        el.addEventListener('pointermove', function(e) {
            var r = el.getBoundingClientRect();
            el.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100) + '%');
            el.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100) + '%');
        });
        el.addEventListener('pointerleave', function() {
            el.style.setProperty('--mx', '50%');
            el.style.setProperty('--my', '0%');
        });
    });
})();

// --- Tab bar: indicador fluido ---
(function() {
    var indicator = document.getElementById('tabIndicator');
    if (!indicator) return;

    var items = document.querySelectorAll('.bottom-nav-item');
    var activeIndex = Array.prototype.indexOf.call(items, document.querySelector('.bottom-nav-item.active'));

    function positionIndicator() {
        if (activeIndex < 0) return;
        indicator.style.transform = 'translateX(' + (activeIndex * 100) + '%)';
    }

    // Move indicator on tab click (progressive enhancement)
    items.forEach(function(item, idx) {
        item.addEventListener('click', function() {
            activeIndex = idx;
            indicator.style.transform = 'translateX(' + (idx * 100) + '%)';
        });
    });

    // Recompute after lucide replaces icons (layout shift)
    if (document.readyState === 'complete') {
        positionIndicator();
    } else {
        window.addEventListener('load', positionIndicator);
    }
})();
