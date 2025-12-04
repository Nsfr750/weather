# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.6.x   | :white_check_mark: |
| < 1.6   | :x:                |

## Reporting a Vulnerability

We take the security of our software seriously. If you discover any security vulnerabilities, please report them to us as soon as possible.

### How to Report a Vulnerability

1. **Email Security Team**: Send an email to [info@tuxxle.org](mailto:info@tuxxle.org) with the subject line: `[Weather App] Security Vulnerability Report`
2. **Provide Details**: Include the following in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Impact assessment
   - Any proof-of-concept code (if available)

### What to Expect

- We will acknowledge receipt of your report within 3 business days
- We will keep you informed about the progress of the vulnerability resolution
- We will credit you in our security advisories (unless you prefer to remain anonymous)
- We aim to provide a fix within 30 days of the report

## Security Best Practices

### For Users
- Always download the application from the official GitHub repository
- Keep your operating system and Python environment updated
- Be cautious when entering API keys or sensitive information
- Only install plugins or extensions from trusted sources

### For Developers
- Follow secure coding practices
- Use the latest stable versions of all dependencies
- Regularly update dependencies to address known vulnerabilities
- Never commit sensitive information to version control
- Use environment variables for API keys and other secrets

## Dependencies

We regularly monitor our dependencies for security vulnerabilities using:
- Dependabot for automated dependency updates
- GitHub Security Alerts
- OWASP Dependency-Check

## Data Protection

### Sensitive Data
- API keys are stored in the user's configuration directory with restricted permissions
- Weather data is cached locally but does not contain personally identifiable information
- Network communications are encrypted using TLS 1.2+

### Permissions
| Permission | Purpose |
|------------|---------|
| Network Access | Fetch weather data and updates |
| File System (Read/Write) | Store configuration and cache data |
| System Tray | Show notifications and quick access |
| Location (optional) | Get weather for current location |

## Security Audits

We conduct regular security audits that include:
- Static code analysis
- Dependency vulnerability scanning
- Manual code reviews
- Penetration testing (for major releases)

## Security Updates

- Security patches are released as patch versions (e.g., 1.6.1 → 1.6.2)
- Critical security updates may be backported to previous versions
- Subscribe to GitHub releases to receive notifications about updates

## Responsible Disclosure

We follow responsible disclosure practices. Please:
- Allow us a reasonable amount of time to address the issue before disclosure
- Do not exploit the vulnerability for malicious purposes
- Do not disclose the vulnerability publicly until we've had a chance to address it

## Contact

For security-related inquiries, please contact:  
**Security Team**: [info@tuxxle.org](mailto:info@tuxxle.org)  

**Note**: For general support questions, please use the [GitHub Issues](https://github.com/Nsfr750/weather/issues) page.
