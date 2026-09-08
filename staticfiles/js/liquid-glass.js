/* Liquid glass - shared behaviour for the auth pages.
   Vanilla JS on purpose: it must not depend on jQuery, which base.html
   loads after the page content. */
(function () {
  'use strict';

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* Specular highlight tracks the pointer across each glass slab. */
  function bindSpecular(card) {
    var spec = card.querySelector('.lg-spec');
    if (!spec || calm.matches) return;

    card.addEventListener('pointermove', function (e) {
      var r = card.getBoundingClientRect();
      spec.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100) + '%');
      spec.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100) + '%');
    });
    card.addEventListener('pointerleave', function () {
      spec.style.setProperty('--mx', '30%');
      spec.style.setProperty('--my', '12%');
    });
  }

  /* Show / hide toggle for any password field marked up with a reveal button. */
  function bindReveal(btn) {
    var field = document.getElementById(btn.getAttribute('aria-controls'));
    if (!field) return;

    btn.addEventListener('click', function () {
      var shown = field.type === 'text';
      field.type = shown ? 'password' : 'text';
      btn.textContent = shown ? 'Show' : 'Hide';
      btn.setAttribute('aria-pressed', shown ? 'false' : 'true');
      field.focus();
    });
  }

  /* Profile circle dropdown toggle */
  function bindProfileDropdown() {
    var toggle = document.getElementById('userProfileDropdownBtn');
    if (!toggle) return;
    var menu = toggle.nextElementSibling;
    if (!menu) return;

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = menu.classList.contains('show');
      menu.classList.toggle('show', !isOpen);
      toggle.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');
    });

    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove('show');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* Fast, delay-free mobile navbar closing & outside-click handling */
  function bindFastMobileNav() {
    var nav = document.getElementById('navbars-rs-food');
    var toggler = document.querySelector('.top-navbar .navbar-toggler');
    var header = document.querySelector('.top-navbar');
    if (!nav || !toggler) return;

    function closeNavImmediately() {
      if (window.jQuery && window.jQuery(nav).hasClass('show')) {
        window.jQuery(nav).collapse('hide');
      } else if (nav.classList.contains('show')) {
        nav.classList.remove('show');
        toggler.classList.add('collapsed');
        toggler.setAttribute('aria-expanded', 'false');
      }
    }

    // 1. Close immediately when tapping any link inside the mobile navbar
    var navLinks = nav.querySelectorAll('.nav-link, a.dropdown-item');
    Array.prototype.forEach.call(navLinks, function (link) {
      link.addEventListener('click', function () {
        if (nav.classList.contains('show')) {
          closeNavImmediately();
        }
      });
    });

    // 2. Close immediately when tapping anywhere outside the navbar
    document.addEventListener('click', function (e) {
      if (nav.classList.contains('show') && header && !header.contains(e.target)) {
        closeNavImmediately();
      }
    });

    // 3. Touchstart listener for instant touch dismiss without 300ms click delay
    document.addEventListener('touchstart', function (e) {
      if (nav.classList.contains('show') && header && !header.contains(e.target)) {
        closeNavImmediately();
      }
    }, { passive: true });
  }

  /* Instant feedback: navbar button turns orange when clicked */
  function bindNavbarClicks() {
    var navLinks = document.querySelectorAll('.top-navbar .navbar-nav .nav-link:not(.lg-nav-logout)');
    Array.prototype.forEach.call(navLinks, function (link) {
      link.addEventListener('click', function () {
        var allItems = document.querySelectorAll('.top-navbar .navbar-nav .nav-item');
        Array.prototype.forEach.call(allItems, function (item) {
          item.classList.remove('active');
          var l = item.querySelector('.nav-link');
          if (l) {
            l.classList.remove('is-current', 'is-clicked', 'active');
          }
        });
        var parentItem = link.closest('.nav-item');
        if (parentItem) {
          parentItem.classList.add('active');
        }
        link.classList.add('is-clicked', 'active');
      });
    });
  }

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('.lg-card, .lg-profile-flyout'), bindSpecular);
    Array.prototype.forEach.call(document.querySelectorAll('.lg-reveal'), bindReveal);
    bindProfileDropdown();
    bindFastMobileNav();
    bindNavbarClicks();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
