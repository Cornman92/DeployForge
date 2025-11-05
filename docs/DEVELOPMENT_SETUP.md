# DeployForge Development Setup Guide

This guide will help you set up your development environment for contributing to DeployForge.

---

## 📋 Prerequisites

### Required Software

1. **Operating System**
   - Windows 10 21H2 or later
   - Windows 11 (recommended)
   - Windows Server 2019/2022
   - ⚠️ **Administrator privileges required**

2. **.NET SDK**
   - .NET 8.0 SDK or later
   - Download: https://dotnet.microsoft.com/download/dotnet/8.0

   ```powershell
   # Verify installation
   dotnet --version  # Should show 8.0.x or later
   ```

3. **Node.js**
   - Node.js 20.x LTS or later
   - Download: https://nodejs.org/

   ```powershell
   # Verify installation
   node --version  # Should show v20.x.x or later
   npm --version   # Should show 10.x.x or later
   ```

4. **PowerShell Core**
   - PowerShell 7.4 or later
   - Download: https://github.com/PowerShell/PowerShell/releases

   ```powershell
   # Verify installation
   $PSVersionTable.PSVersion  # Should show 7.4.x or later
   ```

5. **Git**
   - Git 2.40 or later
   - Download: https://git-scm.com/downloads

   ```powershell
   # Verify installation
   git --version  # Should show 2.40.x or later
   ```

### Recommended Software

1. **IDE/Editor**
   - **Visual Studio 2022** (Community, Professional, or Enterprise)
     - Workloads: ASP.NET and web development, .NET desktop development
     - Download: https://visualstudio.microsoft.com/downloads/

   - **Visual Studio Code** (Recommended for cross-component development)
     - Download: https://code.visualstudio.com/
     - Extensions will be suggested automatically (see `.vscode/extensions.json`)

2. **Windows ADK (Assessment and Deployment Kit)**
   - Required for DISM API and deployment features
   - Download: https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install
   - Components needed:
     - Deployment Tools
     - Windows Preinstallation Environment (Windows PE)
     - User State Migration Tool (USMT)

3. **Database Tools** (Optional)
   - **DB Browser for SQLite**: For viewing local database
   - Download: https://sqlitebrowser.org/

4. **Redis** (For caching, optional for local development)
   - Download: https://github.com/microsoftarchive/redis/releases
   - Or use Docker: `docker run -d -p 6379:6379 redis`

---

## 🚀 Quick Start

### 1. Clone the Repository

```powershell
# Clone the repository
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge

# Create your feature branch
git checkout -b feature/your-feature-name
```

### 2. Backend Setup

```powershell
# Navigate to backend directory
cd src/backend

# Restore NuGet packages
dotnet restore

# Build the solution
dotnet build

# Run tests to verify setup
dotnet test

# Run the API (development mode)
cd DeployForge.Api
dotnet run
```

The API should now be running at `http://localhost:5000` (and `https://localhost:5001`)

### 3. Frontend Setup

```powershell
# Navigate to frontend directory (from repository root)
cd src/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend should now be available at `http://localhost:5173`

### 4. PowerShell Module Setup

```powershell
# Navigate to PowerShell module directory
cd src/powershell

# Import the module for testing
Import-Module .\DeployForge.psd1 -Force

# Verify module loaded
Get-Module DeployForge

# List available commands
Get-Command -Module DeployForge
```

---

## 🔧 Detailed Setup

### Visual Studio Code Setup

1. **Install VS Code**
   - Download and install from https://code.visualstudio.com/

2. **Open the workspace**
   ```powershell
   code .
   ```

3. **Install recommended extensions**
   - VS Code will prompt you to install recommended extensions
   - Or manually install from Extensions panel
   - See `.vscode/extensions.json` for the full list

4. **Configure C# Dev Kit**
   - Install "C# Dev Kit" extension
   - The solution should be automatically detected

5. **Verify setup**
   - Press `Ctrl+Shift+B` to build
   - Press `F5` to debug

### Visual Studio 2022 Setup

1. **Open the solution**
   - Open `src/backend/DeployForge.sln` in Visual Studio

2. **Restore packages**
   - Right-click solution → Restore NuGet Packages

3. **Set startup projects**
   - Right-click solution → Properties → Startup Project
   - Select "Multiple startup projects"
   - Set `DeployForge.Api` to Start

4. **Configure debugging**
   - Press F5 to build and run with debugging

### Database Setup

1. **Initialize SQLite database**
   ```powershell
   cd src/backend/DeployForge.Api

   # Run migrations (when available)
   dotnet ef database update
   ```

2. **Seed data** (optional)
   ```powershell
   # Run with seed data flag
   dotnet run --seed
   ```

### Redis Setup (Optional)

**Option 1: Docker (Recommended)**
```powershell
docker run -d --name deployforge-redis -p 6379:6379 redis
```

**Option 2: Windows Native**
1. Download Redis for Windows
2. Install and start the service
3. Default port 6379 should work out of the box

### Environment Variables

Create a `.env` file in `src/backend/DeployForge.Api/`:

```env
ASPNETCORE_ENVIRONMENT=Development
ConnectionStrings__DefaultConnection=Data Source=deployforge.db
ConnectionStrings__RedisConnection=localhost:6379
DeployForge__WorkingDirectory=C:\DeployForge\Work
DeployForge__MountDirectory=C:\DeployForge\Mount
DeployForge__TempDirectory=C:\DeployForge\Temp
DeployForge__LogDirectory=C:\DeployForge\Logs
```

---

## 🧪 Running Tests

### Backend Tests

```powershell
# Run all tests
dotnet test

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"

# Run specific test project
dotnet test tests/unit/DeployForge.Core.Tests

# Run tests in watch mode
dotnet watch test
```

### Frontend Tests

```powershell
cd src/frontend

# Run tests once
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm run test:coverage

# Run UI test viewer
npm run test:ui
```

### PowerShell Tests

```powershell
cd tests/powershell

# Install Pester if needed
Install-Module -Name Pester -Force -SkipPublisherCheck

# Run all tests
Invoke-Pester

# Run specific test file
Invoke-Pester -Path ./ImageManager.Tests.ps1

# Run with coverage
Invoke-Pester -CodeCoverage ../src/powershell/**/*.ps1
```

---

## 🏗️ Build and Run

### Development Build

```powershell
# Backend
cd src/backend
dotnet build --configuration Debug

# Frontend
cd src/frontend
npm run dev
```

### Production Build

```powershell
# Backend
cd src/backend
dotnet publish -c Release -r win-x64 --self-contained

# Frontend
cd src/frontend
npm run build
npm run build:electron
```

### Run Full Stack

**Option 1: VS Code**
- Press `F5` and select "Full Stack Debug" configuration
- Both backend API and frontend will start

**Option 2: Separate Terminals**

Terminal 1 (Backend):
```powershell
cd src/backend/DeployForge.Api
dotnet run
```

Terminal 2 (Frontend):
```powershell
cd src/frontend
npm run dev
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: "dotnet command not found"
**Solution**: Restart your terminal after installing .NET SDK, or add to PATH manually.

#### Issue: "npm install fails"
**Solution**:
```powershell
# Clear cache
npm cache clean --force
# Delete node_modules and try again
Remove-Item -Recurse -Force node_modules
npm install
```

#### Issue: "DISM API not found"
**Solution**: Install Windows ADK from Microsoft's website.

#### Issue: "Access Denied when mounting images"
**Solution**: Run Visual Studio or VS Code as Administrator.

#### Issue: "Port 5000 already in use"
**Solution**: Change port in `appsettings.json` or kill the process using port 5000.

#### Issue: "TypeScript errors in VS Code"
**Solution**:
```powershell
cd src/frontend
# Reload VS Code window
# Ctrl+Shift+P → "TypeScript: Restart TS Server"
```

### Clean Build

If you encounter persistent issues:

```powershell
# Clean everything
.\scripts\clean-all.ps1

# Or manually:
# Backend
cd src/backend
dotnet clean
Remove-Item -Recurse -Force bin, obj

# Frontend
cd src/frontend
Remove-Item -Recurse -Force node_modules, dist, build
npm install
```

---

## 📚 Additional Resources

### Documentation
- [Master Plan](../MASTER_PLAN.md) - Complete project architecture
- [Technology Stack](../TECHNOLOGY_STACK.md) - Technology decisions
- [Implementation Roadmap](../IMPLEMENTATION_ROADMAP.md) - Development phases
- [Contributing Guidelines](../CONTRIBUTING.md) - How to contribute

### Learning Resources
- [.NET 8 Documentation](https://learn.microsoft.com/en-us/dotnet/)
- [React Documentation](https://react.dev/)
- [Electron Documentation](https://www.electronjs.org/docs)
- [DISM API Reference](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/dism-api)
- [PowerShell Documentation](https://learn.microsoft.com/en-us/powershell/)

### Tools Documentation
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Vite](https://vitejs.dev/)
- [Vitest](https://vitest.dev/)
- [Pester](https://pester.dev/)

---

## 🤝 Getting Help

- **GitHub Discussions**: https://github.com/Cornman92/DeployForge/discussions
- **GitHub Issues**: https://github.com/Cornman92/DeployForge/issues
- **Discord** (coming soon)

---

## ✅ Verification Checklist

Before starting development, verify:

- [ ] .NET SDK 8.0+ installed (`dotnet --version`)
- [ ] Node.js 20+ installed (`node --version`)
- [ ] PowerShell 7.4+ installed (`$PSVersionTable.PSVersion`)
- [ ] Git installed (`git --version`)
- [ ] Repository cloned successfully
- [ ] Backend builds without errors (`dotnet build`)
- [ ] Frontend builds without errors (`npm run build`)
- [ ] All tests pass (`dotnet test`, `npm test`)
- [ ] VS Code extensions installed
- [ ] Can run API locally
- [ ] Can run frontend locally
- [ ] Administrator privileges available
- [ ] Windows ADK installed (for DISM features)

---

**Ready to contribute! 🎉**

Check the [Implementation Roadmap](../IMPLEMENTATION_ROADMAP.md) for current development priorities and the [Contributing Guidelines](../CONTRIBUTING.md) for code standards and workflow.
