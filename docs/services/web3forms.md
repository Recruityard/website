---
service: Web3Forms
vendor: Web3Forms
category: necessary
status: active
owner: Recruityard (access key registered to the Recruityard contact inbox)
added: 2026-10-03
last_reviewed: 2026-10-05
---

# Web3Forms

**What it does for us:** receives the Contact Us form and emails each message to our inbox.
GitHub Pages has no server, so a form service is needed.

## Where it is used

- Pages / features: `contact-us.html` (contact form)
- Code / config: form `action="https://api.web3forms.com/submit"` and the hidden `access_key`
  input in `contact-us.html`; submission handling in `assets/site.js` (Contact form section)
- Dashboard: https://web3forms.com (settings for the access key: spam filter, hCaptcha, domain restriction)

## Data it receives

- From visitors: the form fields (name, email, phone, message, privacy-consent tick) plus IP
  address and browser details of the request.
- Delivered to: our contact inbox by email.
- Legal basis: pre-contractual steps / legitimate interest in answering enquiries (the form has a
  consent checkbox linking to the Privacy Policy).

## Cookies and browser storage

None set by Web3Forms itself. The required hCaptcha check is documented in [hcaptcha.md](hcaptcha.md).

## Consent

Necessary: only runs when a visitor submits the form.

## Links

- Documentation: https://docs.web3forms.com/
- Privacy policy: https://web3forms.com/privacy
- Terms: https://web3forms.com/terms

## Notes

- The access key is **public by design** (it can only send mail to our inbox); it is not a secret.
- "hCaptcha required" is switched on for this key, so the form must include the hCaptcha widget.
- If spam starts: enable the spam filter / restrict the key to `recruityard.com` in the dashboard,
  or create a new key and replace it in `contact-us.html`.
