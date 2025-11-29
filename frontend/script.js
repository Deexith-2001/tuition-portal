const API_BASE_URL = "https://tuition-portal-mzzz.onrender.com"; // backend API URL

const yearEl = document.getElementById("year");
if (yearEl) {
  yearEl.textContent = new Date().getFullYear();
}

const form = document.getElementById("enrollForm");
const msg = document.getElementById("formMessage");

if (form) {
  const submitBtn = form.querySelector('button[type="submit"]');

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!msg) return;

    msg.style.color = "#111827";
    msg.textContent = "Submitting...";

    // Simple client-side validation
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    // Trim all string fields
    for (const key of Object.keys(payload)) {
      if (typeof payload[key] === "string") {
        payload[key] = payload[key].trim();
      }
    }

    const requiredFields = [
      "student_name",
      "student_class",
      "subjects",
      "area",
      "phone",
    ];

    for (const field of requiredFields) {
      if (!payload[field]) {
        msg.style.color = "red";
        msg.textContent = "Please fill in all required fields marked with *.";
        return;
      }
    }

    // Disable button while submitting
    if (submitBtn) {
      submitBtn.disabled = true;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/api/enroll`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      let data = null;
      try {
        data = await res.json();
      } catch {
        // ignore JSON parse errors
      }

      if (!res.ok) {
        // Handle FastAPI validation error (422)
        if (res.status === 422 && data && Array.isArray(data.detail)) {
          const firstError = data.detail[0];
          const field =
            firstError &&
            Array.isArray(firstError.loc) &&
            firstError.loc[firstError.loc.length - 1];
          const msgText = firstError && firstError.msg;

          msg.style.color = "red";
          msg.textContent =
            field && msgText
              ? `Validation error on "${field}": ${msgText}`
              : "Validation error – please check the form fields.";
        } else {
          const detail =
            data && data.detail
              ? typeof data.detail === "string"
                ? data.detail
                : JSON.stringify(data.detail)
              : "Failed to submit. Please try again.";
          throw new Error(detail);
        }
        return;
      }

      msg.style.color = "green";
      msg.textContent = "Submitted successfully! I will contact you soon.";
      form.reset();
    } catch (err) {
      console.error(err);
      msg.style.color = "red";
      msg.textContent =
        "Something went wrong. Please try again or contact me on call/WhatsApp.";
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
      }
    }
  });
}
