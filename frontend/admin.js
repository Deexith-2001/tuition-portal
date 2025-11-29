const API_BASE_URL = "http://127.0.0.1:8000"; // same as main frontend

// 🔐 Simple admin credentials (CHANGE THESE!)
const ADMIN_USERNAME = "Deexithmsd";
const ADMIN_PASSWORD = "Deexith@2001";  // choose your own secure password

// DOM elements
const tbody = document.getElementById("enrollmentsTableBody");
const statusEl = document.getElementById("adminStatus");
const searchInput = document.getElementById("searchInput");
const refreshBtn = document.getElementById("refreshBtn");
const exportBtn = document.getElementById("exportBtn");
const logoutBtn = document.getElementById("logoutBtn");

const loginSection = document.getElementById("loginSection");
const adminSection = document.getElementById("adminSection");
const loginForm = document.getElementById("loginForm");
const loginUsername = document.getElementById("loginUsername");
const loginPassword = document.getElementById("loginPassword");
const loginError = document.getElementById("loginError");

document.getElementById("year").textContent = new Date().getFullYear();

let allEnrollments = [];

// ============ AUTH LOGIC ============

function isLoggedIn() {
  return sessionStorage.getItem("isAdminLoggedIn") === "true";
}

function showLogin() {
  loginSection.style.display = "block";
  adminSection.style.display = "none";
  loginError.textContent = "";
  loginPassword.value = "";
}

function showAdmin() {
  loginSection.style.display = "none";
  adminSection.style.display = "block";
  loadEnrollments();
}

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const user = loginUsername.value.trim();
  const pass = loginPassword.value;

  if (user === ADMIN_USERNAME && pass === ADMIN_PASSWORD) {
    sessionStorage.setItem("isAdminLoggedIn", "true");
    showAdmin();
  } else {
    loginError.textContent = "Invalid username or password.";
  }
});

logoutBtn.addEventListener("click", () => {
  sessionStorage.removeItem("isAdminLoggedIn");
  showLogin();
});

// On page load: decide what to show
if (isLoggedIn()) {
  showAdmin();
} else {
  showLogin();
}

// ============ DATA LOADING / TABLE ============

async function loadEnrollments() {
  if (!statusEl) return; // if not visible yet

  statusEl.textContent = "Loading enrollments...";
  tbody.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE_URL}/api/enrollments`);
    if (!res.ok) {
      throw new Error("Failed to load enrollments");
    }
    const data = await res.json();
    allEnrollments = data;
    renderTable(allEnrollments);
    statusEl.textContent = `Loaded ${data.length} enrollments.`;
  } catch (err) {
    console.error(err);
    statusEl.textContent =
      "Error loading enrollments. Make sure backend is running.";
  }
}

function renderTable(rows) {
  tbody.innerHTML = "";
  if (!rows.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 8;
    td.textContent = "No enrollments yet.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  for (const e of rows) {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${e.id}</td>
      <td>${escapeHtml(e.student_name)}</td>
      <td>${escapeHtml(e.student_class || "")}
          ${e.board ? `<span class="badge">${escapeHtml(e.board)}</span>` : ""}
      </td>
      <td>${escapeHtml(e.subjects || "")}</td>
      <td>${escapeHtml(e.area || "")}</td>
      <td>${escapeHtml(e.phone || "")}</td>
      <td>${escapeHtml(e.preferred_time || "")}</td>
      <td>${formatDate(e.created_at)}</td>
    `;

    tbody.appendChild(tr);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatDate(iso) {
  if (!iso) return "";
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toISOString().replace("T", " ").replace("Z", "");
  } catch {
    return iso;
  }
}

// search / filter
if (searchInput) {
  searchInput.addEventListener("input", () => {
    const q = searchInput.value.toLowerCase().trim();
    if (!q) {
      renderTable(allEnrollments);
      return;
    }
    const filtered = allEnrollments.filter((e) => {
      return (
        (e.student_name && e.student_name.toLowerCase().includes(q)) ||
        (e.student_class && e.student_class.toLowerCase().includes(q)) ||
        (e.area && e.area.toLowerCase().includes(q)) ||
        (e.subjects && e.subjects.toLowerCase().includes(q)) ||
        (e.board && e.board.toLowerCase().includes(q)) ||
        (e.phone && e.phone.toLowerCase().includes(q))
      );
    });
    renderTable(filtered);
  });
}

// refresh button
if (refreshBtn) {
  refreshBtn.addEventListener("click", () => {
    loadEnrollments();
  });
}

// export CSV
if (exportBtn) {
  exportBtn.addEventListener("click", () => {
    if (!allEnrollments.length) {
      alert("No enrollments to export.");
      return;
    }
    const header = [
      "id",
      "student_name",
      "student_class",
      "board",
      "subjects",
      "area",
      "phone",
      "preferred_time",
      "created_at",
    ];
    const rows = allEnrollments.map((e) =>
      header
        .map((h) =>
          (e[h] ?? "")
            .toString()
            .replace(/"/g, '""')
        )
        .join(",")
    );
    const csv = [header.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "enrollments.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
}
