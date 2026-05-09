// ── Menu filter tabs ──────────────────────────────────────────────────────────

document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const filter = btn.dataset.filter;

    // Update active button
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    // Show/hide rows and section titles
    document.querySelectorAll(".menu-row").forEach(row => {
      if (filter === "all" || row.dataset.tags === filter) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });

    // Show/hide section titles based on whether any visible rows follow
    document.querySelectorAll(".menu-section-title").forEach(title => {
      if (filter === "all") {
        title.style.display = "";
        return;
      }
      // Find sibling rows after this title until the next title
      let el = title.nextElementSibling;
      let hasVisible = false;
      while (el && !el.classList.contains("menu-section-title")) {
        if (el.classList.contains("menu-row") && el.style.display !== "none") {
          hasVisible = true;
          break;
        }
        el = el.nextElementSibling;
      }
      title.style.display = hasVisible ? "" : "none";
    });
  });
});

// ── Navbar scroll effect ──────────────────────────────────────────────────────

window.addEventListener("scroll", () => {
  const nav = document.querySelector(".navbar");
  if (nav) {
    nav.style.borderBottomColor = window.scrollY > 40
      ? "rgba(196,145,58,0.25)"
      : "rgba(196,145,58,0.15)";
  }
});

// ── Hamburger menu ────────────────────────────────────────────────────────────

const hamburger = document.getElementById("hamburger");
const navLinks  = document.getElementById("nav-links");

if (hamburger && navLinks) {
  hamburger.addEventListener("click", () => {
    hamburger.classList.toggle("open");
    navLinks.classList.toggle("open");
  });

  // Close menu when a link is clicked
  navLinks.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => {
      hamburger.classList.remove("open");
      navLinks.classList.remove("open");
    });
  });
}