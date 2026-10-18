/* ============================================================
   SpendWise — app.js
   Theme · Sidebar · Eye toggle · Category prediction (ML+Keyword)
   Confetti · PWA · Filter pills
   ============================================================ */

(function () {
  'use strict';

  /* ============================================================
     THEME (with auto system detection)
     ============================================================ */
  const root = document.documentElement;
  const savedTheme = localStorage.getItem('sw-theme');

  function getSystemTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark' : 'light';
  }

  const initialTheme = savedTheme || getSystemTheme();
  root.setAttribute('data-bs-theme', initialTheme);

  function paintThemeIcon(theme) {
    document.querySelectorAll('#themeToggle i').forEach(function (i) {
      i.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars';
    });
  }
  paintThemeIcon(initialTheme);

  // Auto-switch when user hasn't manually set preference
  if (!savedTheme && window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
      if (!localStorage.getItem('sw-theme')) {
        const t = e.matches ? 'dark' : 'light';
        root.setAttribute('data-bs-theme', t);
        paintThemeIcon(t);
      }
    });
  }

  /* ============================================================
     👁️ EYE TOGGLE — bulletproof, runs 3 times for safety
     ============================================================ */
  function initEyeToggles() {
    const toggles = document.querySelectorAll('.eye-toggle');

    toggles.forEach(function (btn) {
      if (btn.dataset.eyeBound === '1') return;
      btn.dataset.eyeBound = '1';

      btn.addEventListener('click', function (ev) {
        ev.preventDefault();
        ev.stopPropagation();

        let input = null;

        const sel = btn.getAttribute('data-target');
        if (sel) {
          try { input = document.querySelector(sel); } catch (e) {}
        }
        if (!input) {
          const name = btn.getAttribute('data-field-name');
          if (name) input = document.querySelector('input[name="' + name + '"]');
        }
        if (!input && btn.parentElement) {
          input = btn.parentElement.querySelector('input');
        }
        if (!input) return;

        const showing = input.type === 'text';
        input.type = showing ? 'password' : 'text';

        const icon = btn.querySelector('i');
        if (icon) icon.className = showing ? 'bi bi-eye' : 'bi bi-eye-slash';
        btn.classList.toggle('active', !showing);

        input.focus();
        const len = input.value.length;
        try { input.setSelectionRange(len, len); } catch (e) {}
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEyeToggles);
  } else {
    initEyeToggles();
  }
  setTimeout(initEyeToggles, 300);
  setTimeout(initEyeToggles, 1000);

  /* ============================================================
     GLOBAL CLICK HANDLER
     ============================================================ */
  document.addEventListener('click', function (e) {

    // Theme toggle
    if (e.target.closest('#themeToggle')) {
      const next = root.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-bs-theme', next);
      localStorage.setItem('sw-theme', next);
      paintThemeIcon(next);
      return;
    }

    // Sidebar toggle (mobile)
    if (e.target.closest('#sidebarToggle')) {
      document.getElementById('sidebar').classList.toggle('show');
      document.getElementById('sidebarBackdrop').classList.toggle('show');
      return;
    }

    // Sidebar backdrop close
    if (e.target.closest('#sidebarBackdrop')) {
      document.getElementById('sidebar').classList.remove('show');
      e.target.closest('#sidebarBackdrop').classList.remove('show');
      return;
    }

    // Quick amount chips
    const quick = e.target.closest('.quick-amt');
    if (quick) {
      const input = document.getElementById('id_amount');
      if (input) {
        input.value = quick.dataset.amt;
        input.focus();
        input.classList.add('is-valid');
        setTimeout(function () { input.classList.remove('is-valid'); }, 900);
      }
      return;
    }
  });

  /* ============================================================
     LIVE CATEGORY PREDICTION (ML + Keyword hybrid)
     ============================================================ */
  const form = document.getElementById('expenseForm');
  const titleInput = document.getElementById('id_title');
  const categorySelect = document.getElementById('id_category');
  const badge = document.getElementById('predictBadge');

  if (form && titleInput && badge) {
    const url = form.dataset.predictUrl;
    let timer = null;
    let lastQuery = '';

    titleInput.addEventListener('input', function () {
      const value = titleInput.value.trim();
      clearTimeout(timer);

      if (value.length < 3) {
        badge.classList.add('d-none');
        return;
      }
      if (value === lastQuery) return;

      timer = setTimeout(function () {
        lastQuery = value;
        fetch(url + '?q=' + encodeURIComponent(value), {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
          .then(function (r) { return r.json(); })
          .then(function (data) {
            badge.classList.remove('d-none');

            const methodBadge = data.method === 'ml'
              ? ' <span class="method-tag ml">🧠 ML</span>'
              : ' <span class="method-tag kw">📚 Keyword</span>';

            badge.innerHTML =
              '<i class="bi ' + data.icon + '"></i> Predicted category: ' +
              '<strong>' + data.category + '</strong>' +
              (data.confidence ? ' &middot; ' + data.confidence + '% match' : '') +
              methodBadge;

            // Auto-select only if user hasn't picked manually
            if (categorySelect && !categorySelect.value && data.category !== 'Other') {
              categorySelect.value = data.category;
              categorySelect.classList.add('is-valid');
            }
          })
          .catch(function () { /* silent */ });
      }, 320);
    });
  }

  /* ============================================================
     AUTO-DISMISS ALERTS
     ============================================================ */
  document.querySelectorAll('.app-alert').forEach(function (el) {
    setTimeout(function () {
      if (window.bootstrap && bootstrap.Alert) {
        bootstrap.Alert.getOrCreateInstance(el).close();
      }
    }, 4500);
  });

  /* ============================================================
     CONFETTI on success messages
     ============================================================ */
  if (document.querySelector('.alert-success') && window.confetti) {
    setTimeout(function () {
      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.3 },
        colors: ['#6366f1', '#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b']
      });
    }, 250);
  }

  /* ============================================================
     FILTER PILL PERSIST
     ============================================================ */
  const filterForm = document.getElementById('filterForm');
  if (filterForm) {
    filterForm.addEventListener('submit', function () {
      const hidden = filterForm.querySelector('input[name="period"]');
      if (!hidden) {
        const url = new URL(window.location.href);
        const period = url.searchParams.get('period') || 'all';
        const i = document.createElement('input');
        i.type = 'hidden';
        i.name = 'period';
        i.value = period;
        filterForm.appendChild(i);
      }
    });
  }

  /* ============================================================
     PWA — SERVICE WORKER REGISTRATION
     ============================================================ */
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/static/sw.js')
        .then(function (reg) {
          console.log('[PWA] Service Worker registered:', reg.scope);
        })
        .catch(function (err) {
          console.warn('[PWA] Service Worker registration failed:', err);
        });
    });
  }

  /* ============================================================
     PWA — INSTALL PROMPT
     ============================================================ */
  let deferredPrompt = null;
  const installBanner = document.getElementById('installPrompt');
  const installBtn = document.getElementById('installBtn');
  const dismissInstall = document.getElementById('dismissInstall');

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    if (installBanner && !localStorage.getItem('sw-install-dismissed')) {
      installBanner.classList.remove('d-none');
    }
  });

  if (installBtn) {
    installBtn.addEventListener('click', function () {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then(function (choice) {
        if (choice.outcome === 'accepted') {
          console.log('[PWA] User installed app');
          if (installBanner) installBanner.classList.add('d-none');
        }
        deferredPrompt = null;
      });
    });
  }

  if (dismissInstall) {
    dismissInstall.addEventListener('click', function () {
      if (installBanner) installBanner.classList.add('d-none');
      localStorage.setItem('sw-install-dismissed', '1');
    });
  }

})();