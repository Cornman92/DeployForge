# Changelog

All notable changes to DeployForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 1 - Foundation (In Progress)

## [1.0.0-alpha.3] - 2025-11-05

### Added

#### Frontend Foundation (React + Electron)
- Electron main process with window management and IPC handlers
- Preload script with secure context bridge
- Vite build configuration with path aliases
- TypeScript configuration with strict mode
- Tailwind CSS 3 with custom design system
- ESLint and Prettier configuration
- Complete React 18 application structure
- Redux Toolkit state management with 3 slices (images, components, settings)
- API service layer with Axios
- Custom React hooks (useRedux)

#### UI Components
- Layout component with Sidebar and Header
- Responsive sidebar navigation with 7 routes
- Custom titlebar with window controls
- Dark/light theme support via CSS variables

#### Application Pages
- Dashboard with system status and quick actions
- Image Manager for mounting/unmounting images
- Components page for Windows component management
- Registry Editor page
- Deployment page (USB creation, autounattend)
- Workflows page showing 4 pre-built templates
- Settings page with theme and configuration

#### State Management
- Images slice: image tracking, mounting status, current image
- Components slice: component list, filtering, categories
- Settings slice: theme, API URL, directories, preferences

#### Services
- Complete API service with 15+ methods
- Image operations (mount, unmount, info)
- Component operations (list, remove)
- Workflow operations (list, execute, status)
- Health check and system info

### Technical Details
- TypeScript strict mode enabled
- Path aliases for clean imports (@components, @pages, etc.)
- IPC communication between Electron and renderer
- File selection dialogs
- Window controls (minimize, maximize, close)
- Proper error handling and logging
- Axios interceptors for request/response logging

## [1.0.0-alpha.2] - 2025-11-05

### Added

#### Development Infrastructure
- GitHub issue templates (bug report, feature request, documentation)
- Pull request template with comprehensive checklist
- EditorConfig for code consistency across all file types
- VS Code workspace settings and configurations
- VS Code debug configurations for full-stack debugging
- VS Code tasks for build, test, and run operations
- Recommended VS Code extensions list
- Complete development setup guide (DEVELOPMENT_SETUP.md)
- Contributing guidelines (CONTRIBUTING.md)

#### Backend Core Implementation
- ASP.NET Core 8 API with Program.cs entry point
- Serilog integration (console + rolling file logging)
- Swagger/OpenAPI documentation
- SignalR hub for real-time progress updates
- Service configuration with DI
- Redis cache with in-memory fallback
- Health check endpoints
- CORS configuration for frontend

#### Common Layer
- OperationResult<T> generic result pattern
- String extension methods
- Error handling utilities

#### DISM Engine
- DismManager class with thread-safe DISM initialization
- WIM image mounting/unmounting
- Image information retrieval
- Mounted images enumeration
- DISM session management
- IDisposable pattern for proper cleanup

#### Project Files
- All 8 backend .csproj files configured
- Correct project references and dependencies
- NuGet packages specified

### Technical Highlights
- Production-ready error handling
- Thread-safe operations
- Async/await patterns throughout
- XML documentation for public APIs
- Platform-specific code annotations
- Nullable reference types enabled

## [1.0.0-alpha.1] - 2025-11-05

### Added

#### Project Foundation
- Initial repository structure
- Complete project directory hierarchy
- .gitignore with comprehensive exclusions
- README.md with project overview

#### Documentation
- MASTER_PLAN.md (59KB) - Complete architecture and 200+ features
- TECHNOLOGY_STACK.md (23KB) - All technology decisions
- IMPLEMENTATION_ROADMAP.md - 40-week development plan
- 4 pre-built workflow templates:
  - Gaming Optimized Windows 11
  - Enterprise Security Hardened
  - Minimal/Tiny11 Style
  - Developer Optimized Workstation

#### CI/CD Infrastructure
- GitHub Actions workflow for CI (build, test, security scan)
- GitHub Actions workflow for releases
- Automated testing pipeline
- Code quality analysis (SonarCloud)
- Security scanning (Snyk, Trivy)

#### Backend Structure
- .NET 8 solution file (DeployForge.sln)
- 8 backend project structures:
  - DeployForge.Api
  - DeployForge.Core
  - DeployForge.Common
  - DeployForge.DismEngine
  - DeployForge.ImageManager
  - DeployForge.RegistryEditor
  - DeployForge.Workflow
  - DeployForge.Testing

#### Frontend Structure
- package.json with complete dependency stack
- Project directory structure

#### PowerShell Module
- Module manifest (DeployForge.psd1)
- Module file (DeployForge.psm1)
- Sample cmdlet (Mount-DFImage.ps1)
- Public/Private function structure

#### Configuration
- appsettings.json with comprehensive settings
- Database connection strings
- DISM configuration
- Security settings
- Performance settings
- Feature flags

---

## Release Notes

### Alpha Release Focus

**Phase 1 Progress: ~50% Complete**

This alpha release establishes the complete development infrastructure and implements:
- ✅ Backend API foundation with DISM integration
- ✅ Frontend React + Electron application
- ✅ State management and routing
- ✅ Development tooling and CI/CD
- ⏳ TUI implementation (pending)
- ⏳ PowerShell cmdlets (pending)
- ⏳ Integration tests (pending)

### Known Limitations (Alpha)

- No actual image mounting yet (API endpoints not connected to DISM)
- Components list not populated from real images
- Workflows don't execute yet
- No real-time progress updates
- USB creation not implemented
- Autounattend generator not implemented
- No authentication/authorization
- Limited error handling in UI

### Next Steps (Phase 1 Week 4)

- Implement TUI with blessed framework
- Complete PowerShell cmdlets
- Add integration tests
- Connect UI to backend APIs
- Add E2E smoke tests
- Begin Phase 2: Core Features

---

[Unreleased]: https://github.com/Cornman92/DeployForge/compare/v1.0.0-alpha.3...HEAD
[1.0.0-alpha.3]: https://github.com/Cornman92/DeployForge/compare/v1.0.0-alpha.2...v1.0.0-alpha.3
[1.0.0-alpha.2]: https://github.com/Cornman92/DeployForge/compare/v1.0.0-alpha.1...v1.0.0-alpha.2
[1.0.0-alpha.1]: https://github.com/Cornman92/DeployForge/releases/tag/v1.0.0-alpha.1
