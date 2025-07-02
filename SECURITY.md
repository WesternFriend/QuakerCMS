# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within QuakerCMS, please send an email to the maintainers. All security vulnerabilities will be promptly addressed.

**Please do not report security vulnerabilities through public GitHub issues.**

### What to include in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### Response Timeline

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide a detailed response within 72 hours indicating next steps
- We will work with you to understand and resolve the issue
- We will notify you when the issue is fixed

## Security Best Practices

QuakerCMS follows Django and Wagtail security best practices:

- Regular dependency updates
- Secure default configurations
- Input validation and sanitization
- CSRF protection
- XSS prevention
- SQL injection prevention

## Responsible Disclosure

We follow responsible disclosure practices and ask that security researchers do the same. We will acknowledge security researchers who report vulnerabilities to us in a responsible manner.
