# DeployForge

**The Ultimate Windows Image Configurator, Creator, and Deployment Platform**

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Build Status](https://github.com/Cornman92/DeployForge/workflows/build/badge.svg)](https://github.com/Cornman92/DeployForge/actions)
[![Version](https://img.shields.io/badge/version-1.0.0--alpha-green.svg)](https://github.com/Cornman92/DeployForge/releases)

---

## 🚀 Overview

DeployForge is a comprehensive, enterprise-grade Windows image customization and deployment platform that enables IT professionals and Windows enthusiasts to create, customize, optimize, and deploy Windows installations with unprecedented ease and flexibility.

### Key Features

- **Universal Image Support**: ISO, WIM, ESD, VHDX, VHD, IMG, PPKG
- **Dual Interface**: Modern GUI + Advanced TUI
- **Comprehensive Customization**: Components, drivers, updates, registry tweaks
- **Intelligent Automation**: Visual workflow designer + pre-built templates
- **Built-in Testing**: Automated VM testing and validation
- **Enterprise Ready**: MDT/SCCM integration, compliance profiles
- **AI-Powered**: Optimization recommendations and conflict detection
- **Extensible**: Plugin architecture with RESTful API

---

## 📋 Quick Start

### GUI Mode
```powershell
# Launch DeployForge
deployforge
```

### TUI Mode (Terminal)
```powershell
# Launch TUI
deployforge --tui
```

### PowerShell Module
```powershell
# Import module
Import-Module DeployForge

# Mount and customize image
$session = Mount-DFImage -Path "C:\ISOs\Win11.iso" -Index 1
Remove-DFComponent -Session $session -Name "OneDrive", "Xbox Services"
Set-DFRegistryTweak -Session $session -Preset "GamingOptimized"
Dismount-DFImage -Session $session -Save
```

---

## 📚 Documentation

### User Guides

- **[Getting Started](docs/user-guide/GETTING_STARTED.md)** - Quick start guide for new users
- **[User Guide](docs/user-guide/USER_GUIDE.md)** - Complete feature documentation
- **[Configuration Guide](docs/user-guide/CONFIGURATION_GUIDE.md)** - Advanced configuration options
- **[Troubleshooting](docs/user-guide/TROUBLESHOOTING.md)** - Common issues and solutions

### Technical Documentation

- **[Master Plan](MASTER_PLAN.md)** - Complete project architecture and roadmap
- **[Technology Stack](TECHNOLOGY_STACK.md)** - Technical decisions and justifications
- **[Option B Features](docs/OPTION_B_FEATURES.md)** - Backend API documentation for advanced features
- **[Development Setup](docs/DEVELOPMENT_SETUP.md)** - Developer environment setup

---

## 🛠️ Development Status

This project is currently in **ACTIVE DEVELOPMENT** following a comprehensive 40-week development plan.

**Current Phase**: Phase 1 - Foundation (Weeks 1-4)

### Roadmap Highlights

- ✅ **Phase 1**: Core infrastructure and basic image operations
- 🔄 **Phase 2**: Component management and customization features
- ⏳ **Phase 3**: Advanced image operations (all formats)
- ⏳ **Phase 4**: Deployment tools (USB, autounattend, network)
- ⏳ **Phase 5**: Automation and workflows
- ⏳ **Phase 6**: Testing framework
- ⏳ **Phase 7**: Innovative features (AI, templates, live modification)
- ⏳ **Phase 8**: Plugin system and extensibility
- ⏳ **Phase 9**: Enterprise features
- ⏳ **Phase 10**: Polish and optimization

See [MASTER_PLAN.md](MASTER_PLAN.md) for complete details.

---

## 🤝 Contributing

We welcome contributions from the community! This project is being developed with a "100-developer team" methodology, focusing on:

- Production-grade code quality
- Comprehensive testing (90%+ coverage)
- Extensive documentation
- Industry best practices

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

DeployForge builds upon inspiration from:
- NTLite, MSMG Toolkit, WIM Witch, DISMTools
- Chris Titus Tech debloating scripts
- Schneegans.de autounattend generator
- Rufus/Ventoy USB creation tools

---

**Made with ❤️ for the Windows Deployment Community**

*Empowering Windows Deployment, One Image at a Time*
