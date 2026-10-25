// ====================================
// NOVERA — interface behaviour
// ====================================

(function () {
    'use strict';

    var THEME_KEY = 'novera-theme';

    /* ------------------------------------------------------------------
       Theme
       ------------------------------------------------------------------ */

    function currentTheme() {
        return document.documentElement.getAttribute('data-bs-theme') === 'dark'
            ? 'dark'
            : 'light';
    }

    function applyTheme(theme) {
        var isDark = theme === 'dark';
        document.documentElement.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');

        var meta = document.querySelector('meta[name="theme-color"]');
        if (meta) {
            meta.setAttribute('content', isDark ? '#0e1512' : '#1d4d3f');
        }

        var toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.setAttribute(
                'aria-label',
                isDark ? 'Switch to light theme' : 'Switch to dark theme'
            );
            toggle.setAttribute('title', isDark ? 'Switch to light theme' : 'Switch to dark theme');
        }
    }

    function initializeTheme() {
        applyTheme(currentTheme());

        var toggle = document.getElementById('themeToggle');
        if (!toggle) {
            return;
        }

        toggle.addEventListener('click', function () {
            var next = currentTheme() === 'dark' ? 'light' : 'dark';

            try {
                localStorage.setItem(THEME_KEY, next);
            } catch (error) {
                /* Ignore unavailable storage. */
            }

            applyTheme(next);
        });

        // Follow the system preference only when the reader has not chosen.
        if (window.matchMedia) {
            var query = window.matchMedia('(prefers-color-scheme: dark)');

            var sync = function (event) {
                var stored = null;
                try {
                    stored = localStorage.getItem(THEME_KEY);
                } catch (error) {
                    /* Ignore. */
                }

                if (stored !== 'light' && stored !== 'dark') {
                    applyTheme(event.matches ? 'dark' : 'light');
                }
            };

            if (typeof query.addEventListener === 'function') {
                query.addEventListener('change', sync);
            }
        }
    }

    /* ------------------------------------------------------------------
       Sticky navigation
       ------------------------------------------------------------------ */

    function initializeNavigation() {
        var nav = document.getElementById('siteNav');
        if (!nav) {
            return;
        }

        var update = function () {
            nav.classList.toggle('is-scrolled', window.scrollY > 8);
        };

        update();
        window.addEventListener('scroll', update, { passive: true });
    }

    /* ------------------------------------------------------------------
       Alerts — only quiet confirmations fade away on their own
       ------------------------------------------------------------------ */

    function initializeAlerts() {
        var alerts = document.querySelectorAll('.nv-toast.alert-success, .nv-toast.alert-info');

        alerts.forEach(function (alert) {
            window.setTimeout(function () {
                if (typeof bootstrap !== 'undefined') {
                    bootstrap.Alert.getOrCreateInstance(alert).close();
                } else {
                    alert.remove();
                }
            }, 5200);
        });
    }

    /* ------------------------------------------------------------------
       Reveal on scroll
       ------------------------------------------------------------------ */

    function initializeReveal() {
        var items = Array.prototype.slice.call(document.querySelectorAll('.reveal'));

        if (!items.length) {
            return;
        }

        var reducedMotion = window.matchMedia
            && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        if (reducedMotion || !('IntersectionObserver' in window)) {
            items.forEach(function (item) {
                item.classList.add('is-visible');
            });
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) {
                    return;
                }

                var parent = entry.target.parentElement;
                var siblings = parent
                    ? Array.prototype.slice.call(parent.querySelectorAll(':scope > .reveal'))
                    : [];
                var index = Math.max(0, siblings.indexOf(entry.target));

                entry.target.style.transitionDelay = Math.min(index, 4) * 70 + 'ms';
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            });
        }, {
            threshold: 0.08,
            rootMargin: '0px 0px -40px 0px'
        });

        items.forEach(function (item) {
            observer.observe(item);
        });

        // Safety net: never leave content permanently hidden if an
        // intersection is missed (fast scrolling, print, older browsers).
        window.setTimeout(function () {
            items.forEach(function (item) {
                item.classList.add('is-visible');
                observer.unobserve(item);
            });
        }, 6000);
    }

    /* ------------------------------------------------------------------
       Search field feedback
       ------------------------------------------------------------------ */

    function initializeSearchForm() {
        var search = document.querySelector('[name="q"]');

        if (!search) {
            return;
        }

        search.addEventListener('input', function () {
            this.classList.toggle('has-value', this.value.length > 0);
        });
    }

    /* ------------------------------------------------------------------
       Star rating picker
       ------------------------------------------------------------------ */

    function initializeRatingPickers() {
        document.querySelectorAll('[data-rating-input]').forEach(function (wrapper) {
            var input = wrapper.querySelector('input[type="number"]');
            var stars = Array.prototype.slice.call(wrapper.querySelectorAll('.nv-star'));
            var form = wrapper.closest('form');
            var hint = form ? form.querySelector('[data-rating-hint]') : null;

            if (!input || !stars.length) {
                return;
            }

            function paint(score) {
                stars.forEach(function (star) {
                    var value = Number(star.dataset.score);
                    star.classList.toggle('is-active', value <= score);
                    star.setAttribute('aria-pressed', value <= score ? 'true' : 'false');
                });
            }

            function describe(score) {
                if (!hint) {
                    return;
                }

                if (!score) {
                    hint.textContent = 'No rating selected yet';
                    return;
                }

                hint.textContent = score + ' out of 5 star' + (score === 1 ? '' : 's') + ' selected';
            }

            function commit(score) {
                input.value = score;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                paint(score);
                describe(score);
            }

            stars.forEach(function (star) {
                var score = Number(star.dataset.score);

                star.addEventListener('click', function () {
                    commit(score);
                });

                star.addEventListener('mouseenter', function () {
                    paint(score);
                });
            });

            wrapper.addEventListener('mouseleave', function () {
                paint(Number(input.value) || 0);
            });

            input.addEventListener('input', function () {
                var score = Math.max(0, Math.min(5, Number(input.value) || 0));
                paint(score);
                describe(score);
            });

            paint(Number(input.value) || 0);
            describe(Number(input.value) || 0);
        });
    }

    /* ------------------------------------------------------------------
       Drag and drop for cover uploads
       ------------------------------------------------------------------ */

    function initializeFileDrops() {
        document.querySelectorAll('[data-file-drop]').forEach(function (drop) {
            var input = drop.querySelector('input[type="file"]');

            if (!input) {
                return;
            }

            ['dragenter', 'dragover'].forEach(function (type) {
                drop.addEventListener(type, function (event) {
                    event.preventDefault();
                    drop.classList.add('is-dragover');
                });
            });

            ['dragleave', 'drop'].forEach(function (type) {
                drop.addEventListener(type, function (event) {
                    event.preventDefault();
                    drop.classList.remove('is-dragover');
                });
            });

            drop.addEventListener('drop', function (event) {
                var files = event.dataTransfer && event.dataTransfer.files;

                if (!files || !files.length) {
                    return;
                }

                input.files = files;
                input.dispatchEvent(new Event('change', { bubbles: true }));
            });
        });
    }

    /* ------------------------------------------------------------------
       Smooth scrolling for in-page anchors
       ------------------------------------------------------------------ */

    function initializeSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
            anchor.addEventListener('click', function (event) {
                var href = this.getAttribute('href');

                if (!href || href === '#') {
                    return;
                }

                var target = document.querySelector(href);

                if (!target) {
                    return;
                }

                event.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });

                if (history.replaceState) {
                    history.replaceState(null, '', href);
                }
            });
        });
    }

    /* ------------------------------------------------------------------
       Bootstrap tooltips
       ------------------------------------------------------------------ */

    function initializeTooltips() {
        if (typeof bootstrap === 'undefined') {
            return;
        }

        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (element) {
            new bootstrap.Tooltip(element);
        });
    }

    /* ------------------------------------------------------------------
       Native form validation styling
       ------------------------------------------------------------------ */

    function initializeFormValidation() {
        document.querySelectorAll('form').forEach(function (form) {
            // The permanent-delete form has its own confirmation flow.
            if (form.action && form.action.includes('/delete/')) {
                return;
            }

            // The compact search form does not need validation styling.
            if (form.classList.contains('nv-filter')) {
                return;
            }

            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }

                form.classList.add('was-validated');
            });
        });
    }

    /* ------------------------------------------------------------------
       Password visibility toggles
       ------------------------------------------------------------------ */

    function initializePasswordToggles() {
        document.querySelectorAll('[data-password-toggle]').forEach(function (button) {
            var wrapper = button.closest('.nv-password');
            var input = wrapper ? wrapper.querySelector('input') : null;
            var icon = button.querySelector('i');

            if (!input) {
                return;
            }

            button.addEventListener('click', function () {
                var show = input.type === 'password';

                input.type = show ? 'text' : 'password';
                button.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
                button.setAttribute('aria-pressed', show ? 'true' : 'false');

                if (icon) {
                    icon.classList.toggle('fa-eye', !show);
                    icon.classList.toggle('fa-eye-slash', show);
                }
            });
        });
    }

    /* ------------------------------------------------------------------
       Global boot
       ------------------------------------------------------------------ */

    document.addEventListener('DOMContentLoaded', function () {
        initializeTheme();
        initializeNavigation();
        initializeAlerts();
        initializeReveal();
        initializeSearchForm();
        initializeRatingPickers();
        initializeFileDrops();
        initializeSmoothScroll();
        initializeTooltips();
        initializeFormValidation();
        initializePasswordToggles();
    });

    /* ------------------------------------------------------------------
       Utilities kept for template convenience
       ------------------------------------------------------------------ */

    function formatNumber(number) {
        return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    function showLoading(element) {
        element.classList.add('loading');
        element.innerHTML = '<span class="spinner"></span> Loading…';
    }

    function hideLoading(element, text) {
        element.classList.remove('loading');
        element.textContent = text;
    }

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text)
            .then(function () {
                showToast('Copied to clipboard!', 'success');
            })
            .catch(function (error) {
                console.error('Clipboard error:', error);
                showToast('Failed to copy', 'danger');
            });
    }

    function showToast(message, type) {
        var container = document.querySelector('.toast-container');

        if (!container) {
            return;
        }

        var toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-' + (type || 'info');
        toast.setAttribute('role', 'alert');
        toast.innerHTML =
            '<div class="d-flex">' +
                '<div class="toast-body">' + message + '</div>' +
                '<button type="button" class="btn-close btn-close-white me-2 m-auto" ' +
                'data-bs-dismiss="toast" aria-label="Close"></button>' +
            '</div>';

        container.appendChild(toast);

        if (typeof bootstrap !== 'undefined') {
            new bootstrap.Toast(toast).show();
        }
    }

    function confirmAction(message) {
        return window.confirm(message);
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function debounce(func, wait) {
        var timeout;

        return function () {
            var args = arguments;
            var context = this;

            window.clearTimeout(timeout);
            timeout = window.setTimeout(function () {
                func.apply(context, args);
            }, wait);
        };
    }

    function throttle(func, limit) {
        var waiting = false;

        return function () {
            var args = arguments;
            var context = this;

            if (waiting) {
                return;
            }

            func.apply(context, args);
            waiting = true;

            window.setTimeout(function () {
                waiting = false;
            }, limit);
        };
    }

    function isInViewport(element) {
        var rect = element.getBoundingClientRect();

        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    function getUrlParameter(name) {
        name = name.replace(/[\[\]]/g, '\\$&');
        var results = new RegExp('[?&]' + name + '=([^&#]*)').exec(location.search);

        return results === null
            ? ''
            : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    window.NoveraUtils = {
        formatNumber: formatNumber,
        showLoading: showLoading,
        hideLoading: hideLoading,
        copyToClipboard: copyToClipboard,
        showToast: showToast,
        confirmAction: confirmAction,
        formatDate: formatDate,
        debounce: debounce,
        throttle: throttle,
        isInViewport: isInViewport,
        getUrlParameter: getUrlParameter
    };
})();
