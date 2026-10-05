# 0002. Use Web3Forms for the contact form

- Status: accepted
- Date: 2026-10-04

## Context

Without Framer, the contact form had nowhere to send submissions; GitHub Pages has no server.
Options: Web3Forms, Formspree, a Zoho form embed, or a plain `mailto:` link.

## Decision

Web3Forms: free tier (250 submissions/month), no account needed, public access key, emails go to our
inbox. hCaptcha is required on the key to block spam.

## Consequences

- Form fields and IP address are processed by Web3Forms and hCaptcha (see `services/`).
- The access key is public by design; if abused, rotate it.
- Submissions are emails, not records in Zoho.
