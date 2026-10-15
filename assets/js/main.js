/* =========================================================
   UCCL — site behaviour
   Sticky nav, mobile menu, active section highlight,
   scroll reveals, stat counters, contact form handling.
   ========================================================= */
(function () {
  "use strict";

  /**
   * Optional: set to a form endpoint (e.g. Formspree, Basin, Netlify Forms URL)
   * to POST submissions to your inbox. When empty, the form validates and
   * shows a confirmation without leaving the page (demo mode).
   */
  var FORM_ENDPOINT = "";

  /* ---------- Sticky header shadow ---------- */
  var header = document.getElementById("site-header");

  function onScroll() {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 8);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile menu ---------- */
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("primary-nav");

  if (toggle && header && nav) {
    toggle.addEventListener("click", function () {
      var open = header.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });

    // Close the menu after a link is chosen
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        header.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
      }
    });

    // Close on Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && header.classList.contains("nav-open")) {
        header.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  /* ---------- Scroll reveal animations ---------- */
  var revealEls = Array.prototype.slice.call(document.querySelectorAll(".reveal"));

  if ("IntersectionObserver" in window && revealEls.length) {
    var revealObserver = new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    revealEls.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- Animated stat counters ---------- */
  var stats = Array.prototype.slice.call(document.querySelectorAll(".stat__value[data-count]"));
  var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function formatNumber(n, thousands) {
    var s = String(Math.round(n));
    return thousands ? s.replace(/\B(?=(\d{3})+(?!\d))/g, ",") : s;
  }

  function animateStat(el) {
    var target = parseFloat(el.getAttribute("data-count")) || 0;
    var suffix = el.getAttribute("data-suffix") || "";
    var useThousands = el.getAttribute("data-format") === "thousands";
    var duration = 1400;
    var start = null;

    function step(ts) {
      if (start === null) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      // ease-out cubic — fast start, gentle settle
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = formatNumber(target * eased, useThousands) + suffix;
      if (progress < 1) window.requestAnimationFrame(step);
    }
    window.requestAnimationFrame(step);
  }

  if (stats.length && "IntersectionObserver" in window && !prefersReduced) {
    var statObserver = new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateStat(entry.target);
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.6 }
    );
    stats.forEach(function (el) { statObserver.observe(el); });
  }

  /* ---------- Active nav link highlighting ---------- */
  var sectionIds = ["about", "services", "why-uccl", "coverage", "leadership", "contact"];
  var sections = sectionIds
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav__link"));

  function setActiveLink(id) {
    navLinks.forEach(function (link) {
      var match = link.getAttribute("href") === "#" + id;
      link.classList.toggle("is-active", match);
    });
  }

  if ("IntersectionObserver" in window && sections.length) {
    var sectionObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) setActiveLink(entry.target.id);
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach(function (sec) { sectionObserver.observe(sec); });
  }

  /* ---------- Contact form ---------- */
  var form = document.getElementById("contact-form");
  var status = document.getElementById("form-status");
  var submitBtn = document.getElementById("cf-submit");

  function showFieldError(input, show) {
    var errorEl = document.getElementById(input.id + "-error");
    input.classList.toggle("is-invalid", show);
    input.setAttribute("aria-invalid", show ? "true" : "false");
    if (errorEl) errorEl.hidden = !show;
  }

  function validateField(input) {
    var value = (input.value || "").trim();
    var valid = true;

    if (input.hasAttribute("required") && value === "") valid = false;
    if (valid && input.type === "email" && value !== "") {
      valid = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
    }
    if (valid && input.type === "tel" && value !== "") {
      valid = /^[+()\-\s\d]{7,20}$/.test(value);
    }

    showFieldError(input, !valid);
    return valid;
  }

  if (form) {
    var fields = Array.prototype.slice.call(
      form.querySelectorAll("input[required], textarea[required], input[type='email'], input[type='tel']")
    );

    // Re-validate on input once a field has errored (so errors clear as the user types)
    fields.forEach(function (input) {
      input.addEventListener("input", function () {
        if (input.classList.contains("is-invalid")) validateField(input);
      });
      input.addEventListener("blur", function () {
        if ((input.value || "").trim() !== "") validateField(input);
      });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      var allValid = fields.map(validateField).every(Boolean);
      if (!allValid) {
        if (status) {
          status.textContent = "Please complete the highlighted fields and try again.";
          status.className = "form-status is-error";
        }
        var firstInvalid = form.querySelector(".is-invalid");
        if (firstInvalid) firstInvalid.focus();
        return;
      }

      var payload = {
        name: form.name.value.trim(),
        company: form.company.value.trim(),
        email: form.email.value.trim(),
        phone: form.phone.value.trim(),
        message: form.message.value.trim()
      };

      if (submitBtn) {
        submitBtn.classList.add("is-loading");
        submitBtn.disabled = true;
      }
      if (status) {
        status.textContent = "Sending your enquiry…";
        status.className = "form-status";
      }

      function succeed() {
        form.reset();
        if (submitBtn) {
          submitBtn.classList.remove("is-loading");
          submitBtn.disabled = false;
        }
        if (status) {
          status.textContent =
            "Thank you, " + payload.name.split(" ")[0] +
            ". Your enquiry has been received — a member of our leadership team will contact you within one business day.";
          status.className = "form-status is-success";
        }
      }

      function fail() {
        if (submitBtn) {
          submitBtn.classList.remove("is-loading");
          submitBtn.disabled = false;
        }
        if (status) {
          status.textContent =
            "We could not send your message automatically. Please email info@uccl.com.bd or call +880 1711-000000.";
          status.className = "form-status is-error";
        }
      }

      if (FORM_ENDPOINT) {
        fetch(FORM_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(payload)
        })
          .then(function (res) { res.ok ? succeed() : fail(); })
          .catch(fail);
      } else {
        // Demo mode: no endpoint configured — confirm locally after a short delay
        window.setTimeout(succeed, 700);
      }
    });
  }

  /* ---------- Eased smooth scrolling for anchor navigation ---------- */
  function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  function headerOffset() {
    return (header ? header.offsetHeight : 74) + 14;
  }

  document.addEventListener("click", function (e) {
    var link = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!link) return;
    var hash = link.getAttribute("href");
    if (!hash || hash === "#") return;
    var target = document.querySelector(hash);
    if (!target) return;

    e.preventDefault();

    var startY = window.pageYOffset;
    var endY = Math.max(0, target.getBoundingClientRect().top + startY - headerOffset());
    var distance = endY - startY;

    if (prefersReduced || Math.abs(distance) < 2) {
      window.scrollTo(0, endY);
      if (history.replaceState) history.replaceState(null, "", hash);
      return;
    }

    // Take over the motion so CSS scroll-behavior doesn't stack with ours
    var root = document.documentElement;
    var previousBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";

    var duration = Math.min(1100, Math.max(500, Math.abs(distance) * 0.45));
    var startTime = null;

    function glide(ts) {
      if (startTime === null) startTime = ts;
      var progress = Math.min((ts - startTime) / duration, 1);
      window.scrollTo(0, startY + distance * easeInOutCubic(progress));
      if (progress < 1) {
        window.requestAnimationFrame(glide);
      } else {
        root.style.scrollBehavior = previousBehavior;
        if (history.replaceState) history.replaceState(null, "", hash);
      }
    }
    window.requestAnimationFrame(glide);
  });

  /* ---------- Pointer-driven 3D card tilt + light sheen ---------- */
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  if (!prefersReduced && finePointer) {
    var tiltEls = document.querySelectorAll(
      ".service-card, .value-card, .team-card, .mv-card, .compliance-card, .logo-tile"
    );
    Array.prototype.forEach.call(tiltEls, function (el) {
      el.classList.add("is-tiltable");

      el.addEventListener("pointermove", function (ev) {
        var rect = el.getBoundingClientRect();
        var px = (ev.clientX - rect.left) / rect.width;
        var py = (ev.clientY - rect.top) / rect.height;
        var rotateY = (px - 0.5) * 7;
        var rotateX = (0.5 - py) * 7;
        el.style.setProperty("--mx", (px * 100).toFixed(1) + "%");
        el.style.setProperty("--my", (py * 100).toFixed(1) + "%");
        el.style.transform =
          "perspective(900px) translateY(-6px) rotateX(" + rotateX.toFixed(2) +
          "deg) rotateY(" + rotateY.toFixed(2) + "deg)";
      });

      el.addEventListener("pointerleave", function () {
        el.style.transform = "";
        el.style.removeProperty("--mx");
        el.style.removeProperty("--my");
      });
    });
  }

  /* ---------- Hero parallax (background depth on scroll) ---------- */
  var heroBg = document.querySelector(".hero__bg");
  if (heroBg && !prefersReduced) {
    var parallaxTicking = false;
    var updateParallax = function () {
      var offset = Math.min(window.pageYOffset * 0.1, 110);
      heroBg.style.transform = "translate3d(0, " + offset + "px, 0)";
      parallaxTicking = false;
    };
    window.addEventListener(
      "scroll",
      function () {
        if (!parallaxTicking) {
          parallaxTicking = true;
          window.requestAnimationFrame(updateParallax);
        }
      },
      { passive: true }
    );
    updateParallax();
  }

  /* ---------- Footer year ---------- */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
})();
