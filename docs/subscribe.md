Email subscription UI (header)
===============================

Summary
-------
Added a compact email subscription form to the site header, styled to match Rat News Network. The form validates email addresses with a simple client-side regex, provides visible invalid-state styling, disables the button while requests are in-flight, and posts the email to the `/api/subscribe` endpoint.

Files changed / added
---------------------
- templates/base.html
  - Replaced the separate `.email-input` and `.menu-button` blocks with a single `.subscribe-container` that includes:
    - `#subscribe-form` with an `<input name="email">` and submit button.
    - `#subscribe-message` for feedback messages.

- templates/site_template/static/styles.css
  - Added styles for:
    - `.subscribe-container`, `.subscribe-form`, `.subscribe-input`, `.subscribe-button`
    - `.subscribe-message` and success/error states
  - Styles reuse existing CSS variables (e.g. `--golden-yellow`, `--deep-black`) and fonts.

- templates/site_template/static/script/subscribe.js (new)
  - Handles:
    - Simple regex validation: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` (client-side convenience only)
    - Toggling `.invalid` class on the input to show red border
    - Disabling/enabling the submit button while sending
    - POSTing `{ email }` as JSON to `/api/subscribe`
    - Showing auto-fading messages for info/success/error for ~4s
    - Graceful handling of network errors and non-2xx API responses

Behavior & constraints
----------------------
- Client-side validation is intentionally permissive; the server must perform authoritative validation.
- The client expects an API at `/api/subscribe`. The repository does not add server-side subscription handling.
- The UI is responsive and will compress the input width on small screens (CSS media rules).

Testing instructions
--------------------
1. Unit tests
   - Run the project's test suite:
     - `pytest`
   - The frontend JS isn't covered by the Python unit tests; `pytest` ensures no Python-side regressions.

2. Manual checks (recommended)
   - Open the site locally (if a dev server is available) or inspect the generated output:
     - Verify the email input appears to the left of the Subscribe button in the header.
     - Enter an invalid email (e.g. `not-an-email`) and confirm the input border turns red and an error message appears.
     - Enter a valid email and submit; confirm the button disables and a "Submitting…" message appears.
     - Simulate API success: the form should reset and show "Success! Check your inbox to confirm."
     - Simulate API failure or network error: an error message should appear with status or network info.
   - Check mobile breakpoints to ensure the header remains usable.

Notes for maintainers
---------------------
- To change the visual theme of the input, prefer editing `templates/site_template/static/styles.css` and use existing CSS variables for consistent colors.
- If you add CSRF protections or change the subscribe endpoint, update `subscribe.js` to include necessary headers/tokens.
