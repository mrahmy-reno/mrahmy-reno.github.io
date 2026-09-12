/* Progressive enhancement only.

   The page is complete and readable without this file:
     - the mobile nav toggle is hidden by CSS unless JS is available, and without JS the
       primary nav list simply stays visible and wraps;
     - every element carries its final geometry and full opacity in the base stylesheet;
       the reveal states are additive and live inside
       `@media (prefers-reduced-motion: no-preference)` + `html.js` (ART_DIRECTION.md 7.3).

   No network requests, no third-party code, no cookies, no storage. Nothing below
   changes layout geometry, so it cannot introduce a layout shift. */
(function () {
  "use strict";

  var root = document.documentElement;
  root.className = root.className.replace("no-js", "js");

  /* ------------------------------------------------------------------ mobile nav */
  var toggle = document.querySelector(".nav-toggle");
  var list = document.getElementById("primary-nav");

  if (toggle && list) {
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        list.classList.add("is-open");
      } else {
        list.classList.remove("is-open");
      }
    };

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });

    list.addEventListener("click", function (event) {
      if (event.target && event.target.tagName === "A") {
        setOpen(false);
      }
    });
  }

  /* --------------------------------------------------- chrome condensation on scroll */
  var header = document.querySelector(".site-header");
  if (header) {
    var condensed = false;
    var onScroll = function () {
      var next = window.scrollY > 24;
      if (next !== condensed) {
        condensed = next;
        header.setAttribute("data-condensed", next ? "true" : "false");
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");
  var motionOk = !(reduced && reduced.matches);

  /* ------------------------------------------------------------------ reveal */
  /* Additive only: the base CSS already shows everything. This walks the page once and
     marks each block as it comes into view; with reduced motion requested nothing is
     marked, because nothing is hidden. */
  if (motionOk && "IntersectionObserver" in window) {
    var targets = document.querySelectorAll("[data-reveal]");
    if (targets.length) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            observer.unobserve(entry.target);
          }
        });
      }, { rootMargin: "0px 0px -15% 0px", threshold: 0.12 });
      Array.prototype.forEach.call(targets, function (el) { observer.observe(el); });
    }
  }

  /* -------------------------------------------------------------- current section */
  /* aria-current is a static, non-motion marker (DESIGN_SYSTEM.md §6.5): the nav item
     for the section in view. Only set where the target section exists on this page. */
  var navLinks = document.querySelectorAll(".nav-list a[data-nav-section]");
  if (navLinks.length) {
    var sections = [];
    Array.prototype.forEach.call(navLinks, function (link) {
      var id = link.getAttribute("data-nav-section");
      var el = document.getElementById(id);
      if (el) {
        sections.push({ link: link, el: el });
      }
    });
    if (sections.length) {
      var mark = function () {
        var current = null;
        var i;
        for (i = 0; i < sections.length; i += 1) {
          if (sections[i].el.getBoundingClientRect().top <= 120) {
            current = sections[i].link;
          }
        }
        for (i = 0; i < sections.length; i += 1) {
          if (sections[i].link === current) {
            sections[i].link.setAttribute("aria-current", "true");
          } else {
            sections[i].link.removeAttribute("aria-current");
          }
        }
      };
      var queued = false;
      window.addEventListener("scroll", function () {
        if (queued) { return; }
        queued = true;
        window.requestAnimationFrame(function () { queued = false; mark(); });
      }, { passive: true });
      mark();
    }
  }
})();
