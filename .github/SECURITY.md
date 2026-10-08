# Security Policy

The security of this project is taken seriously. We appreciate your efforts to
responsibly disclose any findings and will make every effort to acknowledge
your contributions.

## Supported Versions

Security updates are provided only for the latest released version of this
library on PyPI. Users are strongly encouraged to keep their installations up
to date.

| Version        | Supported          |
| -------------- | ------------------ |
| Latest release | :white_check_mark: |
| Older releases | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues,
discussions, or pull requests.**

Instead, report them privately through GitHub's private vulnerability
reporting:

[**Report a vulnerability**](https://github.com/hacf-fr/renault-api/security/advisories/new)

When reporting, please include as much of the following as possible:

- A clear description of the vulnerability and its potential impact.
- Steps to reproduce, or a proof of concept.
- Affected version(s) of the library.
- Any known mitigations or workarounds.

Never include real credentials, login tokens, JWTs, VINs or other personal
data in your report; use placeholders instead.

## Disclosure Timeline

- **Acknowledgement:** you will receive an acknowledgement of your report
  within **48 hours**.
- **Initial assessment:** a triage and initial severity assessment will be
  shared within **7 days** of the acknowledgement.
- **Fix and disclosure:** valid reports are targeted for resolution and
  coordinated public disclosure within **90 days** of the initial report,
  depending on complexity and impact.

You will be kept informed throughout the process and credited in the release
notes for the fix, unless you prefer to remain anonymous.

## Out of Scope

The following are **not** considered security vulnerabilities in this project:

- Vulnerabilities in upstream or transitive dependencies. These are handled
  continuously by [Renovate](https://github.com/renovatebot/renovate) and
  addressed through regular dependency updates.
- Issues only reproducible on Python versions older than those listed as
  supported in `pyproject.toml`.
- Issues in the Renault / Dacia / Alpine cloud services (Gigya, Kamereon) or
  in the official MyRenault app; please report those directly to Renault.
  This project is not affiliated with Renault.
- Issues in Home Assistant itself, including its `renault` integration; please
  report those through
  [Home Assistant's security policy](https://www.home-assistant.io/security/).

## Scope

This security policy covers the `renault-api` Python package (library and
CLI) published on [PyPI](https://pypi.org/project/renault-api/) and its source
code in this repository.
