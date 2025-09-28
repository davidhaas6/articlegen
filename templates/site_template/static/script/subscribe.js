/*
Client-side subscription handler for Rat News Network
- Validates email with a simple regex (client-side only)
- Changes input border on invalid
- Disables button while request is in-flight
- POSTs JSON to /api/subscribe
- Shows messages (info/success/error) that auto-fade after 4s
*/

(function () {
  const form = document.getElementById("subscribe-form");
  if (!form) return;
  const input = form.querySelector("input[name='email']");
  const button = form.querySelector("button[type='submit']");
  const msg = document.getElementById("subscribe-message");

  // Simple, permissive email regex (client-side convenience only)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  let hideTimer = null;
  function showMessage(text, type = "info") {
    if (!msg) return;
    msg.textContent = text;
    msg.className = `subscribe-message show ${type}`;
    if (hideTimer) {
      clearTimeout(hideTimer);
    }
    hideTimer = setTimeout(() => {
      if (!msg) return;
      msg.classList.remove("show");
      // keep class type for a moment; could clear text if desired
      msg.textContent = "";
      hideTimer = null;
    }, 4000);
  }

  function setInvalidState(isInvalid) {
    if (!input) return;
    if (isInvalid) {
      input.classList.add("invalid");
      input.setAttribute("aria-invalid", "true");
    } else {
      input.classList.remove("invalid");
      input.removeAttribute("aria-invalid");
    }
  }

  input.addEventListener("input", () => {
    const val = input.value.trim();
    setInvalidState(val.length > 0 && !emailRegex.test(val));
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = input.value.trim();

    // Basic client-side validation
    if (!email || !emailRegex.test(email)) {
      setInvalidState(true);
      showMessage("Invalid email", "error");
      return;
    }

    setInvalidState(false);
    button.disabled = true;
    button.setAttribute("aria-disabled", "true");
    showMessage("Submitting…", "info");

    try {
      const res = await fetch("https://rnn-email-subscribe.davidhaas6.workers.dev/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email }),
      });

      if (!res.ok) {
        // Try to parse JSON or fallback to text
        let text;
        try {
          const data = await res.json();
          text = data.error || JSON.stringify(data);
        } catch (err) {
          text = await res.text().catch(() => res.statusText || "Unknown error");
        }
        showMessage(`Error (${res.status}): ${text}`, "error");
      } else {
        showMessage("Check your inbox!", "success");
        form.reset();
      }
    } catch (err) {
      showMessage("Network error: " + (err && err.message ? err.message : err), "error");
    } finally {
      button.disabled = false;
      button.removeAttribute("aria-disabled");
    }
  });
})();
