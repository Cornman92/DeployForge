# Security Policy

## Supported Versions

The following versions of DeployForge are currently supported with security updates:

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 0.3.x   | :white_check_mark: | Current release |
| 0.2.x   | :white_check_mark: | Maintenance mode |
| 0.1.x   | :x:                | No longer supported |
| < 0.1.0 | :x:                | No longer supported |

## Reporting a Vulnerability

We take security seriously at DeployForge. If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** Open a Public Issue

Please do not open a public GitHub issue for security vulnerabilities. This could put all users at risk.

### 2. Report Privately

Send vulnerability reports to:

**Email**: [Security contact to be added]

For sensitive reports, you may use our PGP key (coming soon).

### 3. Provide Details

Please include the following information in your report:

- **Description**: A clear description of the vulnerability
- **Impact**: What an attacker could do with this vulnerability
- **Affected Versions**: Which versions are affected
- **Reproduction Steps**: Detailed steps to reproduce the vulnerability
- **Proof of Concept**: If possible, include PoC code (but not exploits)
- **Suggested Fix**: If you have ideas on how to fix it
- **Your Contact Info**: So we can follow up with questions

### Example Report Template

```
Subject: [SECURITY] Brief description

Description:
[Detailed description of the vulnerability]

Impact:
[What can an attacker do? Who is affected?]

Affected Versions:
[List versions, e.g., 0.3.0, 0.2.x]

Reproduction Steps:
1. Step 1
2. Step 2
3. Step 3

Proof of Concept:
[Code or steps demonstrating the issue]

Suggested Fix:
[Your suggestions, if any]

Contact:
[Your email/contact info]
```

## Response Timeline

We aim to respond to security reports according to the following timeline:

- **Initial Response**: Within 48 hours
- **Vulnerability Confirmation**: Within 5 business days
- **Fix Development**: Depends on severity and complexity
- **Release**: Coordinated disclosure after fix is ready

### Severity Levels

We classify vulnerabilities using the following severity levels:

#### Critical (CVSS 9.0-10.0)
- Remote code execution
- Authentication bypass
- Privilege escalation to admin
- **Response**: Fix within 48-72 hours

#### High (CVSS 7.0-8.9)
- SQL injection
- Cross-site scripting (XSS)
- Significant data exposure
- **Response**: Fix within 1 week

#### Medium (CVSS 4.0-6.9)
- Denial of service
- Information disclosure
- Insecure defaults
- **Response**: Fix within 2-4 weeks

#### Low (CVSS 0.1-3.9)
- Minor information leaks
- Best practice violations
- **Response**: Fix in next scheduled release

## Security Update Process

When a security vulnerability is confirmed:

1. **Acknowledgment**: We'll acknowledge your report and assign a severity level
2. **Investigation**: Our team will investigate and develop a fix
3. **Patch Development**: We'll create a patch for supported versions
4. **Testing**: Thorough testing to ensure the fix works and doesn't break functionality
5. **Coordinated Disclosure**: We'll coordinate with you on disclosure timing
6. **Release**: We'll release patched versions
7. **Announcement**: We'll publish a security advisory

### Security Advisories

Security advisories will be published at:
- GitHub Security Advisories
- CHANGELOG.md with [SECURITY] tag
- Email notification to registered users (coming soon)

## Vulnerability Disclosure Policy

We practice **coordinated disclosure**:

- We ask security researchers to give us reasonable time to fix vulnerabilities before public disclosure
- We commit to acknowledging and fixing legitimate vulnerabilities promptly
- We will credit reporters in our security advisories (unless you prefer to remain anonymous)

### Preferred Timeline

- **Critical/High**: 30 days before public disclosure
- **Medium**: 60 days before public disclosure
- **Low**: 90 days before public disclosure

If you need an extension, please let us know and we'll work with you.

## Security Best Practices

When using DeployForge, follow these security best practices:

### General Security

1. **Keep Updated**: Always use the latest version
2. **Verify Downloads**: Check SHA256 hashes when downloading
3. **Review Permissions**: Run with minimum required privileges
4. **Audit Logging**: Enable audit logging for compliance

### Image Security

1. **Source Validation**: Only use Windows images from trusted sources
2. **Hash Verification**: Verify image checksums before modification
3. **Backup Original Images**: Always keep unmodified backups
4. **Test in VM**: Test customized images in a VM before deployment

### Configuration Security

1. **Secure Storage**: Store configuration files securely
2. **Credential Management**: Never hardcode credentials
3. **API Keys**: Protect API keys and tokens
4. **Network Security**: Use HTTPS for API communication

### Development Security

1. **Dependency Scanning**: Regularly scan dependencies (we use `safety` and `bandit`)
2. **Code Review**: All PRs require review before merge
3. **Static Analysis**: Code is analyzed with Bandit for security issues
4. **Input Validation**: All user inputs are validated

## Known Security Considerations

### Working with Windows Images

- DeployForge modifies Windows images offline, which requires elevated privileges on Windows
- When mounting images, temporary mount points are created
- Registry modifications are performed in offline registry hives
- File operations use Windows DISM or wimlib tools

### Dependencies

We regularly audit our dependencies for known vulnerabilities:

- `safety check` runs in CI/CD
- Dependabot alerts are enabled
- Critical dependency updates are prioritized

### Platform-Specific Considerations

**Windows**:
- DISM operations require administrator privileges
- Registry operations require appropriate permissions
- PowerShell execution policy may affect some features

**Linux/macOS**:
- wimlib must be installed for WIM/ESD support
- Mounting operations may require sudo access

## Security Features

DeployForge includes several security features:

1. **Audit Logging**: All operations are logged for compliance
2. **Input Validation**: Extensive validation of file paths and parameters
3. **Privilege Checking**: Verifies required permissions before operations
4. **Safe Defaults**: Security-conscious default settings
5. **Error Handling**: Graceful failure without exposing sensitive information

## Scope

### In Scope

Security issues in:
- DeployForge core code
- Official modules and handlers
- Official documentation that could lead to security issues
- Dependencies we directly control
- API and CLI interfaces

### Out of Scope

- Issues in third-party dependencies (report to the respective projects)
- Social engineering attacks
- Physical attacks on hardware
- Issues in modified Windows images themselves (this is user responsibility)
- Vulnerabilities requiring physical access to the machine

## Bug Bounty

We currently do not have a bug bounty program, but we deeply appreciate security researchers who help us keep DeployForge secure. We will:

- Publicly acknowledge your contribution (with your permission)
- List you in our security hall of fame
- Provide a reference letter if requested

## Security Hall of Fame

We thank the following security researchers for responsibly disclosing vulnerabilities:

<!-- Contributors will be listed here -->

*No vulnerabilities have been reported yet.*

## Contact

For security-related questions or concerns:

- **Security Issues**: [Security email to be added]
- **General Security Questions**: Create a GitHub Discussion with the "security" tag
- **Documentation Issues**: Open a regular GitHub issue

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Common Weakness Enumeration](https://cwe.mitre.org/)
- [CVE Common Vulnerabilities and Exposures](https://cve.mitre.org/)

---

**Last Updated**: 2025-11-23

**This policy may be updated periodically. Please check back regularly for the latest version.**
