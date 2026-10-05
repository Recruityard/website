---
service: hCaptcha (via Web3Forms)
vendor: Intuition Machines, Inc.
category: necessary
status: active
owner: managed through the Web3Forms account
added: 2026-10-03
last_reviewed: 2026-10-05
---

# hCaptcha

**What it does for us:** the "I am human" check on the contact form, required by our Web3Forms
settings to block spam.

## Where it is used

- Pages / features: `contact-us.html` only
- Code / config: `<div class="h-captcha" data-captcha="true">` in the form and
  `<script src="https://web3forms.com/client/script.js">` (Web3Forms loads hCaptcha with its own site key);
  `assets/site.js` blocks submission until the box is ticked.

## Data it receives

- From visitors on the contact page: IP address, browser/device signals and interaction data used to
  tell humans from bots.
- Stored: hCaptcha processes data in the US/EU; see its privacy policy.
- Legal basis: legitimate interest (security / spam prevention).

## Cookies and browser storage

hCaptcha may set security cookies on `hcaptcha.com` (for example an accessibility cookie for users who
opted in to its accessibility mode). **Verify** in DevTools after loading the contact page and list
anything found in [../cookies.md](../cookies.md).

## Consent

Necessary (security) — loads on the contact page regardless of the banner choice. It is mentioned in
the banner's "Necessary" description.

## Links

- Documentation: https://docs.hcaptcha.com/
- Web3Forms integration: https://docs.web3forms.com/getting-started/customizations/spam-protection/hcaptcha
- Privacy policy: https://www.hcaptcha.com/privacy

## Notes

hCaptcha shows "localhost detected" when testing locally; test on the live domain.
