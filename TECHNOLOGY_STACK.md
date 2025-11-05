# DeployForge Technology Stack
## Comprehensive Technology Decisions and Justifications

---

## 1. FRONTEND TECHNOLOGIES

### 1.1 GUI Application (Primary Interface)

#### **Framework: Electron 28+**
**Justification:**
- Cross-platform desktop support (future Mac/Linux ports)
- Native OS integration capabilities
- Large ecosystem and community
- Access to Node.js for backend communication
- Rich UI capabilities with web technologies

**Alternatives Considered:**
- WPF (.NET) - Windows-only, less flexible
- Qt - Steeper learning curve
- Tauri - Smaller ecosystem, less mature

#### **Frontend Framework: React 18+**
**Justification:**
- Component-based architecture
- Excellent state management options
- Large talent pool
- Rich ecosystem of libraries
- Server-side rendering capabilities

**Key Libraries:**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "redux": "^5.0.0",
  "@reduxjs/toolkit": "^2.0.0",
  "react-redux": "^9.0.0"
}
```

#### **UI Component Library: shadcn/ui + Radix UI**
**Justification:**
- Modern, accessible components
- Highly customizable
- TypeScript support
- Headless UI architecture
- Excellent documentation

**Styling: Tailwind CSS 3+**
**Justification:**
- Utility-first approach
- Rapid development
- Small production bundle
- Responsive design built-in
- JIT compilation for performance

**Additional UI Libraries:**
```json
{
  "@radix-ui/react-*": "Latest",
  "tailwindcss": "^3.4.0",
  "framer-motion": "^10.16.0",
  "recharts": "^2.10.0",
  "d3": "^7.8.5",
  "react-flow-renderer": "^11.10.0",
  "xterm": "^5.3.0",
  "@xterm/addon-fit": "^0.8.0"
}
```

### 1.2 TUI Application (Terminal Interface)

#### **Primary: Node.js + blessed**
**Justification:**
- Rich terminal UI capabilities
- Good performance for most operations
- Extensive widget library
- Code sharing with GUI (business logic)

**Libraries:**
```json
{
  "blessed": "^0.1.81",
  "blessed-contrib": "^4.11.0",
  "neo-blessed": "^0.2.0",
  "terminal-kit": "^3.0.1"
}
```

#### **Secondary: Go + Bubble Tea (Performance-Critical)**
**For operations requiring maximum performance:**
```go
// go.mod
require (
    github.com/charmbracelet/bubbletea v0.25.0
    github.com/charmbracelet/bubbles v0.17.1
    github.com/charmbracelet/lipgloss v0.9.1
)
```

**Justification:**
- Native performance
- Low memory footprint
- Excellent for CLI tools
- Beautiful TUI capabilities

---

## 2. BACKEND TECHNOLOGIES

### 2.1 Core Backend

#### **Language: C# (.NET 8)**
**Justification:**
- Native Windows integration
- Excellent DISM API bindings
- Strong typing and performance
- Mature ecosystem
- Great tooling (Visual Studio)
- Cross-platform support (.NET Core)

**Framework: ASP.NET Core 8**
**Features Used:**
- Web API for REST endpoints
- SignalR for real-time updates
- Dependency Injection
- Middleware pipeline
- Background services

**Project Structure:**
```
DeployForge.sln
├── src/
│   ├── DeployForge.Core/           # Business logic
│   ├── DeployForge.Api/            # REST API
│   ├── DeployForge.DismEngine/     # DISM wrapper
│   ├── DeployForge.ImageManager/   # Image operations
│   ├── DeployForge.RegistryEditor/ # Registry operations
│   ├── DeployForge.Workflow/       # Workflow engine
│   ├── DeployForge.Testing/        # Test framework
│   └── DeployForge.Common/         # Shared utilities
├── tests/
│   ├── DeployForge.UnitTests/
│   ├── DeployForge.IntegrationTests/
│   └── DeployForge.E2ETests/
```

**NuGet Packages:**
```xml
<ItemGroup>
  <!-- Web Framework -->
  <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.0" />
  <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />

  <!-- ORM & Database -->
  <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
  <PackageReference Include="Microsoft.EntityFrameworkCore.Sqlite" Version="8.0.0" />
  <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.0" />

  <!-- Caching -->
  <PackageReference Include="StackExchange.Redis" Version="2.7.10" />

  <!-- Messaging -->
  <PackageReference Include="RabbitMQ.Client" Version="6.8.1" />

  <!-- Logging -->
  <PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
  <PackageReference Include="Serilog.Sinks.File" Version="5.0.0" />

  <!-- Testing -->
  <PackageReference Include="xUnit" Version="2.6.2" />
  <PackageReference Include="Moq" Version="4.20.70" />
  <PackageReference Include="FluentAssertions" Version="6.12.0" />

  <!-- Windows Integration -->
  <PackageReference Include="Microsoft.Dism" Version="3.0.0" />
  <PackageReference Include="System.Management" Version="8.0.0" />
</ItemGroup>
```

### 2.2 Scripting Layer

#### **PowerShell Core 7.4+**
**Justification:**
- Native Windows automation
- DISM module built-in
- Cross-platform
- Easy for Windows admins
- Excellent COM/WMI support

**PowerShell Modules:**
```powershell
# Required modules
Install-Module -Name DISM
Install-Module -Name Hyper-V
Install-Module -Name Storage
```

**Custom Module Structure:**
```
DeployForge.PowerShell/
├── DeployForge.psd1
├── DeployForge.psm1
├── Public/
│   ├── Image/
│   │   ├── Mount-DFImage.ps1
│   │   ├── Dismount-DFImage.ps1
│   │   └── Get-DFImageInfo.ps1
│   ├── Component/
│   │   ├── Remove-DFComponent.ps1
│   │   ├── Add-DFComponent.ps1
│   │   └── Get-DFComponent.ps1
│   ├── Workflow/
│   │   ├── Start-DFWorkflow.ps1
│   │   ├── Get-DFWorkflow.ps1
│   │   └── New-DFWorkflow.ps1
│   └── Deployment/
│       ├── New-DFBootableUSB.ps1
│       ├── New-DFAutounattend.ps1
│       └── Test-DFImage.ps1
└── Private/
    └── # Helper functions
```

---

## 3. DATA LAYER

### 3.1 Primary Database: SQLite

**Justification:**
- Embedded, no separate server
- Zero configuration
- Perfect for desktop applications
- ACID compliant
- Wide language support

**Schema Design:**
```sql
-- Configuration storage
CREATE TABLE configurations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,
    data JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Image sessions
CREATE TABLE image_sessions (
    id TEXT PRIMARY KEY,
    image_path TEXT NOT NULL,
    image_format TEXT NOT NULL,
    mount_path TEXT,
    status TEXT NOT NULL,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Modifications log
CREATE TABLE modifications (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    type TEXT NOT NULL,
    action TEXT NOT NULL,
    details JSON NOT NULL,
    status TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES image_sessions(id)
);

-- Templates
CREATE TABLE templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    category TEXT,
    configuration JSON NOT NULL,
    author TEXT,
    version TEXT,
    downloads INTEGER DEFAULT 0,
    rating REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Workflows
CREATE TABLE workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    steps JSON NOT NULL,
    variables JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Execution history
CREATE TABLE executions (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    status TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    current_step TEXT,
    logs JSON,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);
```

### 3.2 Cache Layer: Redis

**Justification:**
- In-memory performance
- Pub/Sub for real-time updates
- Session storage
- Background job queue

**Usage Patterns:**
```csharp
// Component cache
redis.Set("components:win11:24H2", components, TimeSpan.FromHours(1));

// Real-time updates
redis.Publish("image:progress", progressData);

// Job queue
redis.ListRightPush("jobs:workflow", workflowData);
```

### 3.3 Optional Cloud Database: PostgreSQL

**For enterprise cloud features:**
- User management
- Team collaboration
- Template marketplace
- Audit logging

---

## 4. WINDOWS INTEGRATION

### 4.1 DISM (Deployment Image Servicing and Management)

#### **C# DISM API**
```csharp
using Microsoft.Dism;

// Initialize DISM
DismApi.Initialize(DismLogLevel.LogErrors);

// Mount image
DismApi.MountImage(
    imageFilePath,
    mountPath,
    imageIndex,
    readOnly: false
);

// Get packages
var packages = DismApi.GetPackages(session);

// Remove package
DismApi.RemovePackage(session, package.PackageName);

// Cleanup
DismApi.UnmountImage(mountPath, commit: true);
DismApi.Shutdown();
```

#### **PowerShell DISM Module**
```powershell
# Mount WIM
Mount-WindowsImage -ImagePath $wimPath -Index 1 -Path $mountPath

# Get features
Get-WindowsOptionalFeature -Path $mountPath

# Remove app
Remove-AppxProvisionedPackage -Path $mountPath -PackageName $pkg

# Dismount
Dismount-WindowsImage -Path $mountPath -Save
```

### 4.2 Windows ADK Integration

**Components Used:**
- WSIM (Windows System Image Manager) - for autounattend.xml
- oscdimg.exe - for ISO creation
- Windows PE - for bootable media

**Programmatic Access:**
```csharp
// Generate autounattend.xml
var wsim = new WindowsSystemImageManager();
wsim.LoadCatalog(wimPath);
wsim.CreateAnswerFile();
wsim.AddComponent("Microsoft-Windows-Shell-Setup");
wsim.Save(outputPath);
```

### 4.3 Registry Manipulation

**Offline Registry Hive Loading:**
```csharp
using Microsoft.Win32;

// Load offline hive
int result = RegLoadKey(
    HKEY_LOCAL_MACHINE,
    "OFFLINE_SOFTWARE",
    $@"{mountPath}\Windows\System32\config\SOFTWARE"
);

// Modify registry
using (var key = Registry.LocalMachine.OpenSubKey(@"OFFLINE_SOFTWARE\Policies", true))
{
    key.SetValue("DisableTelemetry", 1, RegistryValueKind.DWord);
}

// Unload hive
RegUnloadKey(HKEY_LOCAL_MACHINE, "OFFLINE_SOFTWARE");
```

### 4.4 Virtual Hard Disk (VHD/VHDX)

**Mounting VHDX:**
```powershell
# Mount VHDX
Mount-VHD -Path $vhdxPath

# Get drive letter
$disk = Get-VHD -Path $vhdxPath | Get-Disk
$driveLetter = (Get-Partition -DiskNumber $disk.Number).DriveLetter

# Work with mounted drive
# ...

# Dismount
Dismount-VHD -Path $vhdxPath
```

**C# Storage API:**
```csharp
using Microsoft.Management.Infrastructure;

// Mount VHDX
var session = CimSession.Create("localhost");
var mountParams = new CimMethodParametersCollection {
    CimMethodParameter.Create("Path", vhdxPath, CimFlags.None)
};
session.InvokeMethod("Root\\Virtualization\\v2", "Msvm_ImageManagementService", "Mount", mountParams);
```

---

## 5. VIRTUALIZATION & TESTING

### 5.1 QEMU

**Justification:**
- Open-source
- Fast
- Scriptable
- UEFI support
- Snapshot capability

**Usage:**
```bash
qemu-system-x86_64 \
  -m 4096 \
  -smp 2 \
  -hda test-image.vhdx \
  -bios OVMF.fd \
  -display none \
  -serial file:serial.log \
  -vnc :0
```

**C# Integration:**
```csharp
var process = new Process
{
    StartInfo = new ProcessStartInfo
    {
        FileName = "qemu-system-x86_64.exe",
        Arguments = $"-m 4096 -hda {imagePath} -vnc :0",
        UseShellExecute = false,
        RedirectStandardOutput = true
    }
};
process.Start();
```

### 5.2 Hyper-V (Windows-Native)

**PowerShell Integration:**
```powershell
# Create VM
New-VM -Name "DeployForge-Test" -MemoryStartupBytes 4GB -Generation 2

# Attach VHDX
Add-VMHardDiskDrive -VMName "DeployForge-Test" -Path $vhdxPath

# Start VM
Start-VM -Name "DeployForge-Test"

# Get screenshot
Get-VMVideo -VMName "DeployForge-Test" | Save-VMSnapshot
```

### 5.3 Packer (Image Building Automation)

**For automated testing:**
```json
{
  "builders": [{
    "type": "qemu",
    "iso_url": "custom-windows.iso",
    "disk_size": "40960",
    "format": "qcow2",
    "headless": true,
    "boot_wait": "10s"
  }],
  "provisioners": [{
    "type": "shell",
    "scripts": ["test-script.ps1"]
  }]
}
```

---

## 6. BUILD & DEVOPS

### 6.1 Build Tools

#### **Frontend Build: Webpack 5**
```javascript
// webpack.config.js
module.exports = {
  target: 'electron-renderer',
  entry: './src/index.tsx',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader']
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/index.html'
    })
  ]
};
```

#### **Backend Build: MSBuild / dotnet CLI**
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <OutputType>Exe</OutputType>
    <PublishSingleFile>true</PublishSingleFile>
    <SelfContained>true</SelfContained>
    <RuntimeIdentifier>win-x64</RuntimeIdentifier>
  </PropertyGroup>
</Project>
```

### 6.2 CI/CD: GitHub Actions

**Main Workflow:**
```yaml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: 8.0.x

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore

      - name: Test
        run: dotnet test --no-build --verbosity normal --collect:"XPlat Code Coverage"

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Test
        run: npm test -- --coverage

      - name: Build
        run: npm run build

  integration:
    needs: [backend, frontend]
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run integration tests
        run: |
          # Start backend
          # Start frontend
          # Run E2E tests
```

### 6.3 Code Quality Tools

#### **SonarQube**
```yaml
# sonar-project.properties
sonar.projectKey=deployforge
sonar.sources=src
sonar.tests=tests
sonar.cs.opencover.reportsPaths=**/coverage.opencover.xml
sonar.javascript.lcov.reportPaths=**/coverage/lcov.info
```

#### **ESLint + Prettier (Frontend)**
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "plugins": ["@typescript-eslint", "react", "react-hooks"],
  "rules": {
    "no-console": "warn",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

#### **StyleCop (Backend)**
```xml
<PackageReference Include="StyleCop.Analyzers" Version="1.2.0">
  <PrivateAssets>all</PrivateAssets>
  <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
</PackageReference>
```

---

## 7. PACKAGING & DISTRIBUTION

### 7.1 Electron Builder

**Configuration:**
```json
{
  "build": {
    "appId": "io.deployforge.app",
    "productName": "DeployForge",
    "win": {
      "target": ["nsis", "portable", "zip"],
      "icon": "build/icon.ico",
      "requestedExecutionLevel": "requireAdministrator"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    },
    "files": [
      "dist/**/*",
      "backend/**/*",
      "node_modules/**/*"
    ]
  }
}
```

### 7.2 WiX Toolset (MSI Installer)

**For enterprise distribution:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="DeployForge" Language="1033" Version="1.0.0.0"
           Manufacturer="DeployForge" UpgradeCode="YOUR-GUID">
    <Package InstallerVersion="500" Compressed="yes" InstallScope="perMachine" />

    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />

    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="DeployForge" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
  </Product>
</Wix>
```

### 7.3 Chocolatey Package

```powershell
# deployforge.nuspec
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
  <metadata>
    <id>deployforge</id>
    <version>1.0.0</version>
    <title>DeployForge</title>
    <authors>DeployForge Team</authors>
    <description>Windows Image Configurator and Deployment Tool</description>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <tags>windows deployment imaging dism</tags>
  </metadata>
  <files>
    <file src="tools\**" target="tools" />
  </files>
</package>
```

### 7.4 Auto-Update: electron-updater

```typescript
import { autoUpdater } from 'electron-updater';

autoUpdater.checkForUpdatesAndNotify();

autoUpdater.on('update-available', () => {
  // Notify user
});

autoUpdater.on('update-downloaded', () => {
  // Prompt to restart
});
```

---

## 8. TESTING FRAMEWORKS

### 8.1 Backend Testing

**Unit Tests: xUnit**
```csharp
public class ImageManagerTests
{
    [Fact]
    public void MountImage_ValidWim_ReturnsMountPath()
    {
        // Arrange
        var imageManager = new ImageManager();
        var wimPath = "test.wim";

        // Act
        var mountPath = imageManager.Mount(wimPath);

        // Assert
        Assert.NotNull(mountPath);
        Assert.True(Directory.Exists(mountPath));
    }
}
```

**Integration Tests:**
```csharp
public class DismEngineIntegrationTests : IClassFixture<TestImageFixture>
{
    [Fact]
    public async Task RemoveComponent_ValidComponent_Success()
    {
        // Arrange
        var engine = new DismEngine();

        // Act
        var result = await engine.RemoveComponentAsync("OneDrive");

        // Assert
        Assert.True(result.Success);
    }
}
```

### 8.2 Frontend Testing

**Unit Tests: Jest + React Testing Library**
```typescript
import { render, screen } from '@testing-library/react';
import { ImageInfo } from './ImageInfo';

test('renders image information', () => {
  const image = {
    name: 'Windows 11 Pro',
    size: '4.2 GB',
    format: 'WIM'
  };

  render(<ImageInfo image={image} />);

  expect(screen.getByText('Windows 11 Pro')).toBeInTheDocument();
  expect(screen.getByText('4.2 GB')).toBeInTheDocument();
});
```

**E2E Tests: Playwright**
```typescript
import { test, expect } from '@playwright/test';

test('mount image workflow', async ({ page }) => {
  await page.goto('http://localhost:3000');

  await page.click('text=Mount Image');
  await page.setInputFiles('input[type="file"]', 'test.wim');
  await page.click('text=Mount');

  await expect(page.locator('.status')).toHaveText('Mounted');
});
```

### 8.3 PowerShell Testing

**Pester Framework:**
```powershell
Describe 'Mount-DFImage' {
    It 'Mounts a valid WIM file' {
        # Arrange
        $wimPath = 'TestDrive:\test.wim'

        # Act
        $result = Mount-DFImage -Path $wimPath -Index 1

        # Assert
        $result.MountPath | Should -Not -BeNullOrEmpty
        Test-Path $result.MountPath | Should -Be $true
    }
}
```

---

## 9. DOCUMENTATION TOOLS

### 9.1 User Documentation: Docusaurus

```javascript
// docusaurus.config.js
module.exports = {
  title: 'DeployForge',
  tagline: 'Windows Image Configurator',
  url: 'https://docs.deployforge.io',
  baseUrl: '/',
  themeConfig: {
    navbar: {
      title: 'DeployForge',
      items: [
        {to: 'docs/getting-started', label: 'Docs', position: 'left'},
        {to: 'docs/api', label: 'API', position: 'left'},
        {to: 'blog', label: 'Blog', position: 'left'},
      ],
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
        },
      },
    ],
  ],
};
```

### 9.2 API Documentation: Swagger/OpenAPI

```csharp
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "DeployForge API",
        Version = "v1",
        Description = "REST API for Windows Image Management"
    });

    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    c.IncludeXmlComments(xmlPath);
});
```

### 9.3 Component Documentation: Storybook

```typescript
// Button.stories.tsx
import { Button } from './Button';

export default {
  title: 'Components/Button',
  component: Button,
};

export const Primary = {
  args: {
    variant: 'primary',
    children: 'Click me',
  },
};
```

---

## 10. SECURITY

### 10.1 Dependency Scanning

**Snyk:**
```yaml
# .github/workflows/security.yml
- name: Run Snyk
  uses: snyk/actions/dotnet@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

**npm audit:**
```bash
npm audit fix
npm audit --production
```

### 10.2 Static Analysis

**SonarQube Security Rules**
- SQL Injection detection
- XSS vulnerability scanning
- Insecure crypto usage
- Hardcoded credentials

### 10.3 Runtime Security

**Code Signing:**
```powershell
# Sign executable
signtool sign /f certificate.pfx /p password /t http://timestamp.server DeployForge.exe
```

**Sandbox for Plugins:**
```csharp
var appDomain = AppDomain.CreateDomain("PluginSandbox",
    null,
    new AppDomainSetup {
        ApplicationBase = pluginPath,
        DisallowBindingRedirects = true,
        DisallowCodeDownload = true
    },
    permissions);
```

---

## TECHNOLOGY DECISION SUMMARY

| Category | Technology | Primary Reason |
|----------|-----------|----------------|
| GUI Framework | Electron + React | Cross-platform, rich ecosystem |
| TUI Framework | Blessed/Bubble Tea | Terminal UI excellence |
| Backend Language | C# .NET 8 | Windows integration, performance |
| Scripting | PowerShell Core 7.4 | Windows automation native |
| Database | SQLite + PostgreSQL | Embedded + cloud options |
| Cache | Redis | Performance, real-time |
| Testing | xUnit, Jest, Playwright | Comprehensive coverage |
| Build | MSBuild, Webpack | Native toolchains |
| CI/CD | GitHub Actions | Integrated, powerful |
| Packaging | Electron Builder, WiX | Multi-format support |
| Docs | Docusaurus | Modern, searchable |

---

**Document Version:** 1.0
**Last Updated:** 2025-11-05
**Status:** ✓ APPROVED
