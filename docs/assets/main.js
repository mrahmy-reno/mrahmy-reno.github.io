/* Progressive enhancement only.
   The site is fully usable with JavaScript disabled:
     - the mobile nav toggle is `hidden` in the HTML and only revealed here;
     - without this file the primary nav list simply stays visible and wraps.
   No network requests, no third-party code, no cookies, no storage. */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.remove("no-js");
  root.classList.add("js");

  var toggle = document.querySelector(".nav-toggle");
  var list = document.getElementById("primary-nav");
  if (!toggle || !list) {
    return;
  }

  toggle.hidden = false;

  function setOpen(open) {
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    list.classList.toggle("is-open", open);
  }

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
})();
