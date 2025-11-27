# Frequently Asked Questions (FAQ)

Common questions about DeployForge and Windows image customization.

## 📋 Table of Contents

- [General Questions](#general-questions)
- [Features & Capabilities](#features--capabilities)
- [Licensing & Legal](#licensing--legal)
- [Technical Questions](#technical-questions)
- [Troubleshooting](#troubleshooting)
- [Contributing & Community](#contributing--community)

---

## General Questions

### What is DeployForge?

DeployForge is an enterprise-grade tool for customizing Windows deployment images. It allows you to modify Windows installation images (WIM, ESD, ISO) to:
- Remove bloatware
- Pre-install applications
- Configure system settings
- Apply security hardening
- Optimize for specific use cases (gaming, development, enterprise)

Think of it as a "Windows image customization toolkit" that automates tasks that would otherwise require hours of manual configuration.

---

### Who is DeployForge for?

DeployForge is designed for:

- **🏢 IT Administrators**: Deploy standardized Windows images across organizations
- **💻 System Builders**: Create custom Windows installations for clients
- **🎮 Gaming Café Owners**: Build optimized gaming PC images
- **👨‍💻 Developers**: Set up consistent development environments
- **🏠 Power Users**: Create personalized Windows installations
- **🎓 Students/Educators**: Learn about Windows deployment and customization

---

### Is DeployForge free?

Yes! DeployForge is **100% free and open-source** under the [MIT License](LICENSE).

You can:
- ✅ Use it for personal projects
- ✅ Use it for commercial purposes
- ✅ Modify the source code
- ✅ Distribute your modifications

---

### What's the difference between DeployForge and other tools?

| Feature | DeployForge | NTLite | MSMG Toolkit |
|---------|-------------|---------|--------------|
| **Price** | Free (Open Source) | Paid ($45+) | Free |
| **GUI** | Modern PyQt6 | Windows Forms | Scripts |
| **CLI** | Full CLI support | Limited | Scripts only |
| **API** | Python API + REST API | No API | No API |
| **Cross-Platform** | Win/Linux/macOS | Windows only | Windows only |
| **Automation** | Batch, Templates, Profiles | Limited | Manual |
| **Features** | 150+ | ~100 | ~80 |
| **Open Source** | Yes | No | Partially |

---

### Which Windows versions are supported?

DeployForge supports:

- ✅ **Windows 11** (all editions)
- ✅ **Windows 10** (all editions: Home, Pro, Enterprise, LTSC)
- ✅ **Windows Server** (2016, 2019, 2022)
- ✅ **Windows 8/8.1** (legacy support)

Both **x64 (64-bit)** and **x86 (32-bit)** architectures are supported.

---

### Do I need a Windows license?

**Yes.** DeployForge is a customization tool, not a Windows distribution tool.

- You must have a valid Windows license for each installation
- DeployForge does not provide Windows images
- DeployForge does not bypass activation
- You must obtain Windows from Microsoft or authorized channels

---

## Features & Capabilities

### What can DeployForge do?

DeployForge offers **150+ customization features** across 16 categories:

1. **Debloating**: Remove bloatware, unwanted apps
2. **Privacy**: Disable telemetry, tracking, Cortana
3. **Gaming**: Optimize for gaming performance
4. **Developer Tools**: Install dev environments (Python, Node.js, Docker, etc.)
5. **Security**: Apply hardening (BitLocker, CIS Benchmark, DISA STIG)
6. **Visual Customization**: Themes, taskbar, Start Menu
7. **Network**: Configure DNS, firewall, Remote Desktop
8. **Applications**: Install 40+ applications (browsers, Office, creative tools)
9. **Performance**: Optimize services, power plans, storage
10. **And more...**

See [README.md](README.md) for the complete feature list.

---

### Can I install applications during image creation?

Yes! DeployForge can pre-install **40+ applications**, including:

- **Browsers**: Firefox, Chrome, Brave, Edge, Opera, Vivaldi
- **Office**: Microsoft Office, LibreOffice
- **Development**: VS Code, Git, Python, Node.js, Docker
- **Gaming**: Steam, Epic Games, GOG Galaxy, Discord
- **Media**: VLC, OBS Studio, GIMP, Blender, Audacity
- **Utilities**: 7-Zip, PowerToys, Everything Search

Applications are installed during deployment, not baked into the image.

---

### Can DeployForge create bootable USB drives?

**No.** DeployForge customizes Windows images, but does not create bootable media.

**To create bootable USB**:
1. Use DeployForge to customize your `install.wim`
2. Use [Rufus](https://rufus.ie/), [Ventoy](https://www.ventoy.net/), or Windows Media Creation Tool to create bootable USB
3. Replace the `install.wim` in the `sources/` folder with your customized version

---

### Does DeployForge work with Windows Update?

Yes! DeployForge can:
- ✅ Configure Windows Update settings
- ✅ Disable/enable automatic updates
- ✅ Pre-integrate Windows updates (planned feature)
- ✅ Configure update delivery optimization

Note: Updates are still downloaded during Windows installation, not integrated into the image (yet).

---

### Can I use DeployForge for enterprise deployment?

**Absolutely!** DeployForge is designed with enterprise use in mind:

- ✅ **Batch Operations**: Process multiple images in parallel
- ✅ **Templates**: Reusable customization workflows
- ✅ **Audit Logging**: Compliance tracking
- ✅ **Security Hardening**: CIS Benchmark, DISA STIG
- ✅ **Domain Preparation**: Pre-configure for domain join
- ✅ **REST API**: Integrate with existing tools
- ✅ **Profiles**: Standardized configurations (Enterprise, Workstation, etc.)

---

## Licensing & Legal

### Can I use DeployForge commercially?

**Yes!** DeployForge is licensed under the MIT License, which allows commercial use.

You can:
- ✅ Use it in your business
- ✅ Sell services using DeployForge
- ✅ Distribute customized images to clients (with proper Windows licensing)

You must:
- ✅ Include the MIT License in any distribution
- ✅ Maintain copyright notices

---

### Do I need to credit DeployForge?

While not required, we appreciate attribution! If you use DeployForge in a commercial product or service, consider:
- Mentioning DeployForge in documentation
- Linking to the GitHub repository
- Contributing back improvements

---

### Can I modify and redistribute DeployForge?

**Yes!** The MIT License allows you to:
- ✅ Modify the source code
- ✅ Distribute modified versions
- ✅ Use it in proprietary software

You must:
- ✅ Include the original MIT License
- ✅ Include copyright notice

See [LICENSE](LICENSE) for full details.

---

## Technical Questions

### What image formats are supported?

DeployForge supports **6 image formats**:

1. **ISO** - ISO 9660 disk images (read-only)
2. **WIM** - Windows Imaging Format (most common)
3. **ESD** - Electronic Software Download (compressed WIM)
4. **PPKG** - Provisioning Packages
5. **VHD** - Virtual Hard Disk
6. **VHDX** - Virtual Hard Disk v2

Most users work with **WIM files** (install.wim).

---

### Where do I get Windows images?

**Official sources**:
1. **Microsoft**: https://www.microsoft.com/software-download
2. **Volume Licensing Service Center** (VLSC) - For enterprises
3. **Visual Studio Subscriptions** - For developers
4. **Windows Media Creation Tool** - Creates ISO with install.wim

**⚠️ IMPORTANT**: Only use official Microsoft sources. Never download Windows from unofficial sites.

---

### How large are Windows images?

Typical sizes:

- **Original WIM**: 4-5 GB (Windows 11 Pro)
- **After debloating**: 3-4 GB (-20-25%)
- **Extracted ISO**: 8-10 GB
- **Installed Windows**: 20-30 GB

DeployForge can reduce image size by 2-3 GB through aggressive debloating.

---

### How long does customization take?

**Typical times**:

- **Light customization** (registry tweaks, debloat): 5-10 minutes
- **Medium customization** (+ apps, drivers): 15-30 minutes
- **Heavy customization** (+ full dev environment): 30-60 minutes

**Factors affecting time**:
- Image size
- Number of features
- Disk speed (SSD vs HDD)
- CPU performance
- Number of applications to integrate

---

### Can I automate DeployForge?

**Yes!** DeployForge offers multiple automation options:

1. **CLI**: Scriptable command-line interface
2. **Python API**: Full programmatic access
3. **REST API**: HTTP API for integration
4. **Batch Operations**: Process multiple images
5. **Templates**: Reusable customization workflows
6. **Profiles**: Pre-defined configurations

Example automation:
```python
from deployforge import ImageManager
from deployforge.gaming import GamingOptimizer

# Automate gaming build
with ImageManager('install.wim') as manager:
    manager.mount()
    gaming = GamingOptimizer('install.wim')
    gaming.apply_profile('competitive')
    manager.unmount(save_changes=True)
```

---

### Does DeployForge modify my running Windows?

**No!** DeployForge only modifies **offline images**.

- ✅ Safe: Works on unmounted images
- ✅ Non-destructive: Original image untouched (if using --output)
- ✅ Reversible: Can always start over with original image

Your running Windows installation is never touched.

---

### Can I undo changes?

**Best practice**: Always keep a backup of the original image.

If you used `--output`:
```bash
# Original is preserved
deployforge build --input original.wim --output modified.wim
```

If you didn't specify output:
- Changes are written to the original file
- Keep backups before making modifications!

---

## Troubleshooting

### Why do I need admin/sudo privileges?

Windows image operations require elevated privileges to:
- Mount/unmount images
- Modify registry hives
- Inject drivers
- Modify system files

**Windows**: Run PowerShell as Administrator
**Linux/macOS**: Use `sudo deployforge ...`

---

### Why is it slow on my system?

**Common causes**:

1. **Hard Disk Drive (HDD)**:
   - WIM operations are I/O intensive
   - Solution: Use SSD if possible

2. **Large images**:
   - Windows 11 images are 4-5 GB compressed
   - Solution: This is normal; use faster storage

3. **Antivirus**:
   - Real-time scanning slows operations
   - Solution: Temporarily disable or add exclusions

4. **Low RAM**:
   - Need 8 GB+ for best performance
   - Solution: Close other applications

---

### Does DeployForge work in virtual machines?

**Yes!** DeployForge works great in VMs.

**Tested on**:
- ✅ VMware Workstation/Player
- ✅ VirtualBox
- ✅ Hyper-V
- ✅ QEMU/KVM
- ✅ Parallels (macOS)

**Recommendations**:
- Allocate 4 GB+ RAM
- Use SSD storage
- Enable nested virtualization (if testing in nested VMs)

---

### Common error: "wimlib not found"

**Solution**:

```bash
# Ubuntu/Debian
sudo apt-get install wimtools

# macOS
brew install wimlib

# Windows
# DISM is built-in; if error persists, reinstall DeployForge
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.

---

## Contributing & Community

### How can I contribute?

We welcome contributions! You can help by:

1. **Code**: Submit pull requests
2. **Documentation**: Improve guides, tutorials
3. **Testing**: Test new features, report bugs
4. **Translations**: Help translate (planned)
5. **Community**: Answer questions, share builds

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

### How do I report bugs?

Use our bug report template:

1. [Create Bug Report](https://github.com/Cornman92/DeployForge/issues/new?template=bug_report.yml)
2. Provide:
   - DeployForge version
   - Operating system
   - Steps to reproduce
   - Error messages

---

### How do I request features?

Use our feature request template:

1. [Create Feature Request](https://github.com/Cornman92/DeployForge/issues/new?template=feature_request.yml)
2. Describe:
   - What you want to accomplish
   - Why it would be useful
   - How you envision it working

---

### Where can I get help?

**For questions**:
1. [GitHub Discussions](https://github.com/Cornman92/DeployForge/discussions) - Ask questions, share ideas
2. [Question Template](https://github.com/Cornman92/DeployForge/issues/new?template=question.yml) - Submit specific questions

**For bugs**:
- [Bug Report](https://github.com/Cornman92/DeployForge/issues/new?template=bug_report.yml)

**Documentation**:
- [README.md](README.md) - Full documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide

---

### What's the roadmap?

See [ROADMAP.md](ROADMAP.md) and [TODO.md](TODO.md) for:
- Planned features
- Development priorities
- Timeline estimates
- Community requests

**Upcoming (v0.4.0)**:
- Comprehensive testing suite
- Enhanced documentation
- Application installer framework
- Performance optimizations

**Future (v1.0.0+)**:
- Web platform
- Enterprise features
- Additional image formats
- Plugin system

---

## Advanced Questions

### Can I create my own profiles?

**Yes!** (Planned feature)

Currently, you can:
1. Use existing profiles as templates
2. Modify profile code in `src/deployforge/`
3. Create custom Python scripts using the API

Future: Profile editor in GUI and custom profile support.

---

### Can I integrate DeployForge with other tools?

**Yes!** DeployForge provides multiple integration points:

1. **REST API**: HTTP API for remote control
2. **Python API**: Import as library
3. **CLI**: Shell scripting
4. **Batch Operations**: Integrate with existing workflows

**Example integrations**:
- Ansible playbooks
- PowerShell scripts
- CI/CD pipelines (GitHub Actions, Jenkins)
- MDT/SCCM workflows

---

### Does DeployForge support driver injection?

**Yes!** DeployForge can inject drivers into Windows images.

```bash
deployforge drivers add --image install.wim --driver-path /drivers
```

Supports:
- Single driver (.inf files)
- Driver packages (folders with .inf files)
- Recursive driver scanning
- Driver validation

---

### Can I create Windows PE (WinPE) images?

**Yes!** DeployForge supports WinPE customization:

```bash
deployforge winpe create --output boot.wim
deployforge winpe customize --image boot.wim --drivers /drivers
```

Use cases:
- Custom recovery environments
- Network deployment
- Diagnostic tools
- System repair disks

---

### How do I create answer files (unattend.xml)?

DeployForge can generate answer files:

```bash
deployforge unattend create --output unattend.xml \
  --username "User" \
  --auto-logon \
  --skip-oobe
```

Features:
- Skip OOBE (Out of Box Experience)
- Auto-login configuration
- Network settings
- Partition configuration
- Component customization

---

## Still Have Questions?

If your question isn't answered here:

1. **Search existing issues**: https://github.com/Cornman92/DeployForge/issues
2. **Check documentation**: [README.md](README.md)
3. **Ask the community**: [GitHub Discussions](https://github.com/Cornman92/DeployForge/discussions)
4. **Submit a question**: [Question Template](https://github.com/Cornman92/DeployForge/issues/new?template=question.yml)

---

## Additional Resources

- **Installation**: [INSTALLATION.md](INSTALLATION.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Roadmap**: [ROADMAP.md](ROADMAP.md)

---

**Didn't find your answer?** [Ask a question](https://github.com/Cornman92/DeployForge/issues/new?template=question.yml) or [start a discussion](https://github.com/Cornman92/DeployForge/discussions)! We're here to help. 😊
