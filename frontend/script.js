const API_BASE_URL = "http://127.0.0.1:8000"; // change to Render URL after deploy

document.getElementById("year").textContent = new Date().getFullYear();

const form = document.getElementById("enrollForm");
const msg = document.getElementById("formMessage");

if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.style.color = "#111827";
    msg.textContent = "Submitting...";

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    try {
      const res = await fetch(`${API_BASE_URL}/api/enroll`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json().catch(() => null);
      if (!res.ok) {
        const detail = data && data.detail ? data.detail : "Failed to submit";
        throw new Error(detail);
      }

      msg.style.color = "green";
      msg.textContent = "Submitted successfully! I will contact you soon.";
      form.reset();
    } catch (err) {
      console.error(err);
      msg.style.color = "red";
      msg.textContent =
        "Something went wrong. Please try again or contact me on call/WhatsApp.";
    }
  });
}
