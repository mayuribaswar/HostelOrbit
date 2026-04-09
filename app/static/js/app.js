function createChart(el, labels, values, type = "bar") {
  if (!el || !labels.length) return;
  new Chart(el, {
    type,
    data: {
      labels,
      datasets: [{
        label: "Count",
        data: values,
        borderWidth: 2,
        borderColor: "#2563eb",
        backgroundColor: type === "doughnut"
          ? ["#2563eb", "#f59e0b", "#16a34a", "#dc2626", "#7c3aed"]
          : "rgba(37, 99, 235, 0.2)",
        tension: 0.35,
      }],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}

const adminChart = document.getElementById("adminChart");
if (adminChart) {
  createChart(
    adminChart,
    JSON.parse(adminChart.dataset.labels || "[]"),
    JSON.parse(adminChart.dataset.values || "[]"),
  );
  adminChart.parentElement.style.minHeight = "320px";
}

const complaintChart = document.getElementById("complaintChart");
if (complaintChart) {
  const map = JSON.parse(complaintChart.dataset.map || "{}");
  createChart(complaintChart, Object.keys(map), Object.values(map), "doughnut");
  complaintChart.parentElement.style.minHeight = "320px";
}

const wasteChart = document.getElementById("wasteChart");
if (wasteChart) {
  const map = JSON.parse(wasteChart.dataset.map || "{}");
  createChart(wasteChart, Object.keys(map), Object.values(map), "line");
  wasteChart.parentElement.style.minHeight = "320px";
}

const toggleBtn = document.getElementById("sidebarToggle");
const sidebar = document.getElementById("sidebar");
if (toggleBtn && sidebar) {
  toggleBtn.addEventListener("click", () => sidebar.classList.toggle("open"));
  document.addEventListener("click", (event) => {
    if (!sidebar.classList.contains("open")) return;
    const clickedInside = sidebar.contains(event.target) || toggleBtn.contains(event.target);
    if (!clickedInside) sidebar.classList.remove("open");
  });
}

// Auto-dismiss flash messages.
setTimeout(() => {
  document.querySelectorAll(".flash").forEach((el) => {
    el.style.transition = "opacity 0.3s ease";
    el.style.opacity = "0";
    setTimeout(() => el.remove(), 300);
  });
}, 3200);

// Confirmation dialogs for dangerous actions.
document.querySelectorAll("form").forEach((form) => {
  const dangerButton = form.querySelector(".btn.danger");
  if (dangerButton) {
    form.addEventListener("submit", (e) => {
      const ok = window.confirm("Are you sure you want to continue?");
      if (!ok) e.preventDefault();
    });
  }
});

// Better UX: show loading state for submit buttons.
document.querySelectorAll("form button[type='submit'], form .btn").forEach((btn) => {
  const form = btn.closest("form");
  if (!form) return;
  form.addEventListener("submit", () => {
    if (btn.disabled) return;
    btn.dataset.originalText = btn.textContent;
    btn.textContent = "Please wait...";
    btn.disabled = true;
  });
});
