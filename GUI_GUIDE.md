# DeployForge Modern GUI User Guide

**Version**: 1.7.0 / 0.3.0 (Release)
**Last Updated**: 2025-11-15
**Interface**: PyQt6 Modern GUI (Primary Interface)

Welcome to the DeployForge Modern GUI! This guide will help you customize Windows deployment images with our beautiful, intuitive interface featuring **150+ customization options** across **16 categories**.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Loading an Image](#loading-an-image)
4. [Build Page - Feature Selection](#build-page---feature-selection)
5. [Profiles Page - Quick Setups](#profiles-page---quick-setups)
6. [Analyze Page - Image Analysis](#analyze-page---image-analysis)
7. [Settings Page - Configuration](#settings-page---configuration)
8. [Themes - Light & Dark Mode](#themes---light--dark-mode)
9. [Building Your Image](#building-your-image)
10. [Common Workflows](#common-workflows)
11. [Tips & Tricks](#tips--tricks)
12. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
# Install DeployForge
pip install deployforge

# Or from source
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge
pip install -e .
```

### Launching the GUI

**Method 1: Command Line**
```bash
python -m deployforge.gui_modern
```

**Method 2: Python Module**
```bash
deployforge gui
```

**Method 3: Python Script**
```python
from deployforge.gui_modern import main
main()
```

### First Launch

When you first launch DeployForge, you'll see:
1. **Welcome Page** with quick start tutorial
2. **Drag-and-drop area** for loading images
3. **Recent Files** list (empty on first run)
4. **Quick Start Guide** button for this documentation

---

## Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│  DeployForge - Windows Deployment Suite          [- □ X]    │
├──────┬──────────────────────────────────────────────────────┤
│      │                                                       │
│  📁  │             Welcome to DeployForge                   │
│ Welcome                                                      │
│      │     Drag and drop a .wim, .esd, or .iso file here   │
│  🔨  │              to get started!                         │
│ Build│                                                       │
│      │           Recent Files:                              │
│  👤  │           • install.wim (Yesterday)                  │
│ Profiles                                                     │
│      │           [Quick Start Guide]  [Open File...]       │
│  📊  │                                                       │
│ Analyze                                                      │
│      │                                                       │
│  ⚙️  │                                                       │
│Settings                                                      │
│      │                                                       │
└──────┴──────────────────────────────────────────────────────┘
```

### 5 Main Pages

| Page | Icon | Purpose | When to Use |
|------|------|---------|-------------|
| **Welcome** | 📁 | Load images, access recent files | Starting a new build |
| **Build** | 🔨 | Select features and customizations | Customizing your image |
| **Profiles** | 👤 | Choose pre-configured setups | Quick deployment for specific use cases |
| **Analyze** | 📊 | Analyze and compare images | Quality assurance, testing |
| **Settings** | ⚙️ | Configure GUI preferences | Changing theme, preferences |

---

## Loading an Image

### Method 1: Drag and Drop (Recommended)

1. Navigate to **Welcome Page** (first page)
2. **Drag** a `.wim`, `.esd`, or `.iso` file from File Explorer
3. **Drop** it anywhere in the drag zone
4. The image loads automatically and switches to **Build Page**

**Supported Formats**:
- ✅ `.wim` - Windows Imaging Format
- ✅ `.esd` - Electronic Software Download (compressed WIM)
- ✅ `.iso` - ISO 9660 optical disc image

### Method 2: File Browser

1. Click **"Open File..."** button on Welcome Page
2. Browse to your image file
3. Select the file and click **Open**
4. Image loads and GUI switches to Build Page

### Method 3: Recent Files

1. On Welcome Page, find **Recent Files** section
2. Click on a previously loaded file
3. Image loads instantly

### What Happens After Loading?

1. **Image Information** is displayed (format, size, version)
2. **Build Page** opens automatically
3. **Feature checkboxes** become available
4. **Build Button** activates
5. **Progress Bar** appears at bottom

---

## Build Page - Feature Selection

The Build Page is where the magic happens! With **150+ features** organized into **16 categories**, you can customize every aspect of your Windows deployment.

### Feature Categories

#### 🎮 Gaming (15 Features)

Optimize Windows for gaming performance.

**Key Features**:
- ☑️ **Install NVIDIA Drivers** - Latest GeForce drivers
- ☑️ **Install AMD Drivers** - Latest Radeon drivers
- ☑️ **Enable Game Mode** - Windows gaming optimizations
- ☑️ **Install DirectX** - Latest DirectX runtimes
- ☑️ **Install Visual C++ Runtimes** - Required by most games
- ☑️ **Disable Game DVR** - Remove performance overhead
- ☑️ **Optimize Mouse Settings** - Reduce input lag
- ☑️ **Install Discord** - Gaming communication
- ☑️ **Disable Xbox Game Bar** - Remove overlay
- ☑️ **Ultimate Performance Power Plan** - Maximum CPU performance
- ... and 5 more

**Who Should Use This**: Gamers, gaming PC builders, gaming cafes

---

#### 🗑️ Debloat (20 Features)

Remove unnecessary pre-installed applications.

**What Gets Removed**:
- ☑️ **Xbox Apps** (Console Companion, Game Bar, Gaming Services)
- ☑️ **Microsoft Teams** (Chat/consumer version)
- ☑️ **OneDrive** (Cloud storage client)
- ☑️ **Cortana** (Voice assistant)
- ☑️ **Skype** (Messaging app)
- ☑️ **Candy Crush Saga** (Pre-installed game)
- ☑️ **3D Viewer** (3D model viewer)
- ☑️ **Mixed Reality Portal** (VR/AR app)
- ☑️ **Your Phone** (Phone companion)
- ☑️ **Tips** (Windows tips app)
- ... and 10 more bloatware apps

**Who Should Use This**: Everyone wanting a clean Windows install

---

#### 🔒 Privacy (16 Features)

Enhance privacy by disabling telemetry and tracking.

**Privacy Enhancements**:
- ☑️ **Disable Telemetry** - Stop data collection
- ☑️ **Disable Diagnostics** - Disable diagnostic data
- ☑️ **Disable Advertising ID** - Prevent targeted ads
- ☑️ **Block Telemetry IPs** - Firewall rules
- ☑️ **Disable Bing in Search** - Local search only
- ☑️ **Disable Location Tracking** - Location services off
- ☑️ **Disable Activity History** - No timeline tracking
- ☑️ **Disable Lock Screen Ads** - Remove sponsored content
- ☑️ **Disable Feedback Requests** - No popups
- ☑️ **Disable Cloud Clipboard** - Local clipboard only
- ... and 6 more privacy features

**Who Should Use This**: Privacy-conscious users, enterprises

---

#### 🎨 Visual (19 Features)

Customize the Windows user interface.

**Visual Customizations**:
- ☑️ **Enable Dark Mode** - System-wide dark theme
- ☑️ **Classic Context Menus** - Windows 10-style menus
- ☑️ **Show File Extensions** - Display .txt, .exe, etc.
- ☑️ **Show Hidden Files** - Reveal hidden items
- ☑️ **Taskbar Cleanup** - Remove search, task view, widgets
- ☑️ **Disable Widgets** - Remove news feed
- ☑️ **Disable Snap Layouts** - Traditional snapping
- ☑️ **Custom Wallpaper** - Set default wallpaper
- ☑️ **Custom OEM Info** - Branding in System Properties
- ☑️ **Disable Web Search** - Start menu search only
- ... and 9 more visual tweaks

**Who Should Use This**: Power users, system customizers

---

#### 💻 Developer (19 Features)

Set up development environments.

**Development Tools**:
- ☑️ **Install Python 3.12** - Latest Python
- ☑️ **Install Node.js** - JavaScript runtime
- ☑️ **Install Java JDK** - Java development kit
- ☑️ **Install .NET SDK** - .NET development
- ☑️ **Install Git** - Version control
- ☑️ **Install Visual Studio Code** - Code editor
- ☑️ **Install PowerShell 7** - Modern PowerShell
- ☑️ **Install Windows Terminal** - Modern terminal
- ☑️ **Enable WSL2** - Windows Subsystem for Linux
- ☑️ **Install Docker Desktop** - Container platform
- ☑️ **Enable Hyper-V** - Virtualization
- ☑️ **Install PowerToys** - Utilities for power users
- ... and 7 more dev tools

**Who Should Use This**: Developers, programmers, DevOps engineers

---

#### 🏢 Enterprise (12 Features)

Enterprise security and compliance features.

**Enterprise Features**:
- ☑️ **Security Hardening** - CIS/STIG compliance
- ☑️ **Enable AppLocker** - Application whitelisting
- ☑️ **Enable Credential Guard** - Credential protection
- ☑️ **Configure Windows Defender** - Enhanced security
- ☑️ **Firewall Rules** - Enterprise firewall config
- ☑️ **Domain Join Prep** - Prepare for domain
- ☑️ **Install Office 365** - Microsoft Office suite
- ☑️ **Install Microsoft Teams** - Collaboration
- ☑️ **Enable BitLocker** - Disk encryption
- ☑️ **Audit Logging** - Comprehensive logging
- ... and 2 more enterprise features

**Who Should Use This**: IT administrators, enterprises, managed environments

---

#### 🌐 Web Browsers (6 Options)

Install your preferred web browsers.

**Available Browsers**:
- ☑️ **Mozilla Firefox** - Privacy-focused browser
- ☑️ **Google Chrome** - Popular browser
- ☑️ **Brave Browser** - Privacy + crypto rewards
- ☑️ **Microsoft Edge** (Chromium) - Built-in, enhanced
- ☑️ **Opera** - Feature-rich browser
- ☑️ **Vivaldi** - Customizable power-user browser

**Note**: You can select multiple browsers to install them all!

---

#### 📝 Office & Productivity (10 Applications)

Productivity software installation.

**Applications**:
- ☑️ **Microsoft Office 365** - Word, Excel, PowerPoint
- ☑️ **LibreOffice** - Free office suite
- ☑️ **Zoom** - Video conferencing
- ☑️ **Microsoft Teams** - Collaboration
- ☑️ **Slack** - Team messaging
- ☑️ **Notion** - Notes and documentation
- ☑️ **Adobe Acrobat Reader** - PDF viewer
- ☑️ **Notepad++** - Advanced text editor
- ☑️ **7-Zip** - File archiver
- ☑️ **Everything** - Fast file search

---

#### 🎨 Creative & Media (10 Applications)

Creative software for content creators.

**Applications**:
- ☑️ **OBS Studio** - Screen recording/streaming
- ☑️ **GIMP** - Image editing
- ☑️ **Inkscape** - Vector graphics
- ☑️ **Blender** - 3D creation suite
- ☑️ **DaVinci Resolve** - Video editing
- ☑️ **Audacity** - Audio editing
- ☑️ **VLC Media Player** - Media player
- ☑️ **Kdenlive** - Video editor
- ☑️ **ShareX** - Screenshot/screen capture
- ☑️ **Paint.NET** - Simple image editor

---

#### 🎮 Gaming Platforms (7 Platforms)

Install gaming platforms and launchers.

**Platforms**:
- ☑️ **Steam** - Valve's gaming platform
- ☑️ **Epic Games Store** - Epic games launcher
- ☑️ **GOG Galaxy** - DRM-free games
- ☑️ **Origin** - EA games
- ☑️ **Ubisoft Connect** - Ubisoft games
- ☑️ **Battle.net** - Blizzard games
- ☑️ **Xbox App** - Xbox Game Pass for PC

---

#### 🔧 System Utilities (10 Utilities)

Essential system utilities.

**Utilities**:
- ☑️ **7-Zip** - File compression
- ☑️ **CCleaner** - System cleaner
- ☑️ **Everything** - Fast file search
- ☑️ **PowerToys** - Microsoft utilities
- ☑️ **ShareX** - Screenshots/uploads
- ☑️ **TreeSize Free** - Disk space analyzer
- ☑️ **Process Explorer** - Advanced task manager
- ☑️ **Autoruns** - Startup manager
- ☑️ **Windows Terminal** - Modern terminal
- ☑️ **Notepad++** - Text editor

---

#### ⚡ Performance (10 Optimizations)

Performance optimizations and tweaks.

**Optimizations**:
- ☑️ **Disable Superfetch** - Reduce disk usage
- ☑️ **Disable Windows Search Indexing** - Save resources
- ☑️ **Disable Hibernation** - Save disk space
- ☑️ **Disable Startup Delay** - Faster boot
- ☑️ **SSD Optimizations** - Optimize for SSDs
- ☑️ **Disable Print Spooler** - If no printer
- ☑️ **Disable Remote Assistance** - Security
- ☑️ **Disable Windows Update (Temporary)** - Manual control
- ☑️ **Optimize Memory Management** - Better RAM usage
- ☑️ **Disable Background Apps** - Save resources

---

#### 🔌 Services Management (8 Services)

Control Windows services.

**Service Controls**:
- ☑️ **Disable Windows Update Service** - Manual updates
- ☑️ **Disable Print Spooler** - No printing needed
- ☑️ **Disable Diagnostic Services** - Reduce telemetry
- ☑️ **Disable Remote Desktop** - Security
- ☑️ **Disable Windows Search** - Use alternative
- ☑️ **Disable Bluetooth** - If not needed
- ☑️ **Disable Fax Service** - Legacy service
- ☑️ **Disable Tablet Input** - Desktop only

---

#### 🔋 Power Management (5 Options)

Power plan configuration.

**Power Options**:
- ☑️ **Ultimate Performance Plan** - Maximum performance
- ☑️ **Disable Power Throttling** - Consistent performance
- ☑️ **Disable Sleep** - Always on
- ☑️ **Disable Screen Timeout** - Never turn off
- ☑️ **USB Selective Suspend Off** - Prevent USB sleep

---

#### 📁 File Explorer (7 Tweaks)

File Explorer customizations.

**Tweaks**:
- ☑️ **Remove Quick Access** - This PC as default
- ☑️ **Remove Libraries** - Simplified sidebar
- ☑️ **Remove OneDrive** - Clean sidebar
- ☑️ **Remove 3D Objects** - Unnecessary folder
- ☑️ **Show This PC on Desktop** - Quick access
- ☑️ **Classic Sharing Wizard** - Advanced sharing
- ☑️ **Disable Recent Files** - Privacy

---

#### 🌐 Network (13 Features)

Network configuration and optimization.

**Network Features**:
- ☑️ **Set DNS to 1.1.1.1 (Cloudflare)** - Fast DNS
- ☑️ **Set DNS to 8.8.8.8 (Google)** - Alternative DNS
- ☑️ **Disable IPv6** - If not needed
- ☑️ **Enable Network Discovery** - File sharing
- ☑️ **Configure Windows Firewall** - Security rules
- ☑️ **Disable Remote Desktop** - Security
- ☑️ **Enable Remote Desktop** - IT administration
- ☑️ **QoS Packet Scheduler** - Traffic prioritization
- ☑️ **Large Send Offload** - Network performance
- ☑️ **TCP Optimizer** - Better throughput
- ... and 3 more network features

---

### How to Select Features

1. **Browse Categories**: Scroll through all 16 categories
2. **Read Tooltips**: Hover over checkboxes for descriptions
3. **Check Boxes**: Click to enable features you want
4. **Review Selection**: Selected features show checkmarks
5. **Build**: Click **"Build Image"** button when ready

### Search Features

Use the **Search Box** at the top of Build Page to quickly find features:

```
[🔍 Search features...]
```

**Example Searches**:
- Type "nvidia" → Shows NVIDIA driver options
- Type "privacy" → Shows all privacy-related features
- Type "office" → Shows Office installations

---

## Profiles Page - Quick Setups

Don't want to manually select 150 features? Use our **6 pre-configured profiles**!

### Available Profiles

#### 1. 🎮 Gaming Profile (27 Features)

**Perfect For**: Gaming PCs, gaming cafes, streamers

**What's Included**:
- Steam, Epic Games, GOG Galaxy
- NVIDIA/AMD drivers, DirectX
- Ultimate Performance power plan
- Game Mode enabled, DVR disabled
- Debloat: Xbox, Teams, OneDrive removed
- Discord, OBS Studio
- Gaming network optimizations
- Disable unnecessary services

**Use Case**: Building a gaming PC, installing Windows for a gamer

---

#### 2. 💻 Developer Profile (28 Features)

**Perfect For**: Programmers, web developers, DevOps engineers

**What's Included**:
- Python 3.12, Node.js, Java JDK, .NET SDK
- Git, Visual Studio Code
- WSL2, Docker Desktop, Hyper-V
- Windows Terminal, PowerShell 7
- 4 browsers (Firefox, Chrome, Brave, Edge)
- PowerToys, developer utilities
- Network tools
- Performance optimizations

**Use Case**: Setting up a development workstation

---

#### 3. 🏢 Enterprise Profile (24 Features)

**Perfect For**: Corporate environments, managed IT

**What's Included**:
- Security hardening (CIS/STIG baselines)
- AppLocker, Credential Guard, BitLocker
- Windows Defender configuration
- Firewall rules
- Domain join preparation
- Office 365, Microsoft Teams
- OneDrive (for business)
- Audit logging enabled
- Compliance features

**Use Case**: Enterprise desktop deployment

---

#### 4. 📚 Student Profile (23 Features)

**Perfect For**: Students, education institutions

**What's Included**:
- Office suite, multiple browsers
- Privacy controls (moderate level)
- VLC, Spotify, Discord
- Efficient power settings (battery saving)
- OneDrive for file backup
- Debloat unnecessary apps
- Note-taking tools
- Educational software ready

**Use Case**: Student laptops, school computer labs

---

#### 5. 🎨 Creator Profile (27 Features)

**Perfect For**: Content creators, designers, video editors

**What's Included**:
- OBS Studio, GIMP, Inkscape, Blender
- DaVinci Resolve, Audacity, VLC
- GPU optimization for rendering
- Ultimate Performance power plan
- Large file handling optimizations
- Color management
- Storage optimizations
- Creative software suite

**Use Case**: Content creation workstations

---

#### 6. ⚙️ Custom Profile

**Perfect For**: Users with specific needs

**How It Works**:
1. Manually select features on Build Page
2. Save your selection as "Custom Profile"
3. Reuse it later for similar builds

**Use Case**: Unique configurations, specialized setups

---

### How to Use Profiles

1. **Navigate to Profiles Page** (second icon in sidebar)
2. **Read Profile Descriptions** - Each profile shows what's included
3. **Click Profile Card** - Large, visual profile cards
4. **Confirmation** - GUI switches to Build Page with features auto-selected
5. **Review & Customize** - Adjust individual features if needed
6. **Build** - Click "Build Image" button

**Pro Tip**: Start with a profile, then customize! This saves time compared to manual selection.

---

## Analyze Page - Image Analysis

The Analyze Page helps you understand what's in your Windows image.

### Features

#### Image Information

View detailed image metadata:

```
┌─────────────────────────────────────────┐
│ Image Information                        │
├─────────────────────────────────────────┤
│ Format:        WIM                      │
│ Size:          4.2 GB                   │
│ Created:       2025-10-15               │
│ Modified:      2025-11-14               │
│ Compression:   LZX                      │
│ Boot Index:    1                        │
│ Images:        1                        │
└─────────────────────────────────────────┘
```

#### Image Index Information

For multi-index WIM files:

```
Index 1: Windows 11 Pro
  Architecture: x64
  Size: 15.2 GB (uncompressed)
  Description: Windows 11 Professional
  Flags: 9
```

#### File Count

Shows total files and directories in the image.

#### Compare Images

Compare two Windows images:

1. **Load First Image**
2. **Click "Compare with..."**
3. **Select Second Image**
4. **View Differences**:
   - Files only in Image 1
   - Files only in Image 2
   - Different files (modified)
   - Identical files

**Use Case**: Compare before/after customization, verify changes

---

## Settings Page - Configuration

Configure the GUI to your preferences.

### Theme Selection

Choose between Light and Dark themes:

- **Light Theme** 🌞 - Clean, bright interface
- **Dark Theme** 🌙 - Easy on the eyes, modern look

**Setting persists** across sessions!

### Default Output Directory

Set where customized images are saved:

```
Output Directory: C:\DeployForge\Output
                  [Browse...]
```

### Mount Point

Configure temporary mount location:

```
Mount Point: C:\DeployForge\Mount
             [Browse...]
```

### Advanced Options

- ☑️ **Auto-save recent files** - Remember last 10 files
- ☑️ **Show tooltips** - Feature descriptions
- ☑️ **Enable logging** - Debug information
- ☑️ **Check for updates** - Automatic update check

### GUI Preferences

- **Window Position**: Automatically saves and restores
- **Window Size**: Remembers your preferred size
- **Last Page**: Opens to last visited page

---

## Themes - Light & Dark Mode

DeployForge includes beautiful Light and Dark themes.

### Light Theme 🌞

**Colors**:
- Background: Off-white (#FAFAFA)
- Surface: Pure white (#FFFFFF)
- Primary: Microsoft blue (#0078D4)
- Text: Nearly black (#1F1F1F)

**Best For**:
- Daytime use
- Bright environments
- Users preferring light interfaces

### Dark Theme 🌙

**Colors**:
- Background: Dark gray (#1E1E1E)
- Surface: Lighter gray (#252526)
- Primary: Microsoft blue (#0078D4)
- Text: White (#FFFFFF)

**Best For**:
- Night-time use
- Dark environments
- Reducing eye strain
- Modern aesthetic

### Switching Themes

1. Go to **Settings Page**
2. Find **"Theme"** section
3. Click **Light** or **Dark** button
4. Theme changes instantly

**No Restart Required!** Theme persists across sessions.

---

## Building Your Image

### Build Process

1. **Load Image** (Drag-and-drop or Browse)
2. **Select Features** (Build Page or Profile)
3. **Review Selection** - Check selected features
4. **Click "Build Image"** button
5. **Choose Output Location** - Save customized image
6. **Monitor Progress** - Real-time progress bar
7. **View Logs** - Detailed operation logs
8. **Completion** - Success message

### Progress Monitoring

During build, you'll see:

```
┌──────────────────────────────────────────────┐
│  Building Image... 45%                        │
│  [===================>            ]           │
│                                               │
│  Current: Injecting NVIDIA drivers...        │
│  Time Elapsed: 2m 15s                        │
│  Estimated Remaining: 2m 30s                 │
└───────────────────────────────────────────────┘
```

### Build Logs

Real-time logs show:

```
[10:30:15] Starting build process...
[10:30:16] Mounting install.wim...
[10:30:18] Mount successful: C:\DeployForge\Mount
[10:30:20] Removing Xbox apps...
[10:30:25] Xbox apps removed successfully
[10:30:26] Applying privacy tweaks...
[10:30:30] Privacy tweaks applied
[10:30:31] Injecting NVIDIA drivers...
[10:32:45] NVIDIA drivers injected
...
[10:45:00] Build completed successfully!
```

### Cancel Build

Click **"Cancel"** button to stop build at any time.
- Changes made so far will be **rolled back**
- Original image remains **untouched**

---

## Common Workflows

### Workflow 1: Gaming PC Setup

**Goal**: Create a Windows 11 image optimized for gaming

**Steps**:
1. Load `Win11_22H2.wim`
2. Go to **Profiles Page**
3. Click **Gaming Profile** card
4. GUI switches to Build Page with 27 gaming features selected
5. (Optional) Add extra features like browsers
6. Click **"Build Image"**
7. Save as `Win11_Gaming.wim`
8. Use for gaming PC installations

**Time**: ~10-15 minutes

---

### Workflow 2: Enterprise Deployment

**Goal**: Corporate Windows image with security and compliance

**Steps**:
1. Load `Win11_Enterprise.wim`
2. Go to **Profiles Page**
3. Click **Enterprise Profile**
4. Review auto-selected security features
5. Go to **Build Page** → **Network** category
6. Set DNS to corporate DNS servers
7. Go to **Office & Productivity**
8. Ensure Office 365 and Teams are checked
9. Click **"Build Image"**
10. Save as `Win11_Corp_Secure.wim`

**Time**: ~15-20 minutes

---

### Workflow 3: Developer Workstation

**Goal**: Development environment with all tools

**Steps**:
1. Load `Win11_Pro.wim`
2. Go to **Profiles Page**
3. Click **Developer Profile**
4. 28 dev features auto-selected (Python, Node.js, Git, etc.)
5. Go to **Build Page** → **Developer** category
6. Add any missing tools (e.g., specific IDEs)
7. Go to **Creative & Media**
8. Add tools like Postman, Insomnia (API testing)
9. Click **"Build Image"**
10. Save as `Win11_Dev_Full.wim`

**Time**: ~20-25 minutes (larger build)

---

### Workflow 4: Privacy-Focused Personal PC

**Goal**: Clean Windows with maximum privacy

**Steps**:
1. Load `Win11_Home.wim`
2. Go to **Build Page**
3. **Debloat** category: Select all (remove bloatware)
4. **Privacy** category: Select all (maximum privacy)
5. **Visual** category: Enable Dark Mode, classic menus
6. **Browsers**: Firefox, Brave (privacy browsers)
7. **Services**: Disable telemetry services
8. **Network**: Set DNS to Cloudflare (1.1.1.1)
9. Click **"Build Image"**
10. Save as `Win11_Private.wim`

**Time**: ~10 minutes

---

### Workflow 5: Clean & Minimal Install

**Goal**: Smallest possible Windows installation

**Steps**:
1. Load `Win11_Pro.wim`
2. Go to **Build Page**
3. **Debloat** category: Select ALL features
4. **Performance**: Disable indexing, superfetch
5. **Services**: Disable unnecessary services
6. **File Explorer**: Remove Quick Access, libraries
7. Do NOT select any applications to install
8. Click **"Build Image"**
9. Save as `Win11_Minimal.wim`

**Time**: ~8 minutes

**Result**: Bare-bones Windows, ~30% smaller than stock image

---

## Tips & Tricks

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open image file |
| `Ctrl+S` | Save current configuration |
| `Ctrl+B` | Start build process |
| `F5` | Refresh image information |
| `Ctrl+T` | Toggle theme (Light/Dark) |
| `Ctrl+1` | Switch to Welcome Page |
| `Ctrl+2` | Switch to Build Page |
| `Ctrl+3` | Switch to Profiles Page |
| `Ctrl+4` | Switch to Analyze Page |
| `Ctrl+5` | Switch to Settings Page |
| `Esc` | Cancel current operation |

### Speed Up Your Workflow

1. **Use Profiles First**: Start with Gaming/Developer/Enterprise profile
2. **Search Features**: Use search box instead of scrolling
3. **Save Custom Profiles**: Reuse your configurations
4. **Drag-and-Drop**: Faster than file browser
5. **Recent Files**: Quick access to previous images

### Best Practices

1. **Always work on a copy** - Never modify original Windows media
2. **Test builds in VM first** - Before deploying to hardware
3. **Save custom profiles** - For repeatability
4. **Review logs** - Check for errors after build
5. **Compare images** - Verify changes with Analyze Page

### Power User Features

**Batch Tooltip Reading**: Quickly understand all features in a category by hovering over each checkbox.

**Feature Dependencies**: Some features depend on others. DeployForge automatically enables dependencies.

**Undo Last Action**: If build fails, original image is untouched.

---

## Troubleshooting

### Image Won't Load

**Symptoms**: Drag-and-drop doesn't work, file browser shows error

**Solutions**:
1. **Check file format**: Must be `.wim`, `.esd`, or `.iso`
2. **Check file permissions**: Ensure you have read access
3. **Check file integrity**: File may be corrupted
4. **Try file browser**: Instead of drag-and-drop
5. **Check disk space**: Ensure enough free space

---

### Build Fails

**Symptoms**: Build process stops with error, progress bar freezes

**Solutions**:
1. **Check logs**: Read error message in log panel
2. **Insufficient permissions**: Run GUI as Administrator
3. **Disk space**: Ensure enough free space (2x image size)
4. **Corrupted image**: Try different source image
5. **Conflicting features**: Some features may conflict (check logs)

---

### GUI Freezes

**Symptoms**: Interface becomes unresponsive

**Solutions**:
1. **Wait**: Large operations may take time (image mounting)
2. **Cancel operation**: Click Cancel button if available
3. **Restart GUI**: Close and reopen application
4. **Check system resources**: Ensure adequate RAM (8GB+ recommended)

---

### Features Not Working

**Symptoms**: Selected features don't appear in built image

**Solutions**:
1. **Check logs**: Look for skipped features
2. **Platform limitations**: Some features Windows 11 only
3. **Version requirements**: Ensure compatible Windows version
4. **Missing dependencies**: Install required tools (DISM, wimlib)

---

### Theme Not Saving

**Symptoms**: Theme resets to Light on restart

**Solutions**:
1. **Check settings permissions**: Ensure QSettings can write
2. **Antivirus interference**: Allow DeployForge to save settings
3. **Manually set theme**: Settings Page → Theme → Dark → Apply

---

### Slow Performance

**Symptoms**: GUI lags, sluggish response

**Solutions**:
1. **Close other applications**: Free up system resources
2. **Check CPU/RAM usage**: Task Manager
3. **Update PyQt6**: `pip install --upgrade PyQt6`
4. **Check disk I/O**: SSD recommended for best performance

---

## Getting Help

### Resources

- **Documentation**: Full docs in `docs/` folder
- **GitHub Issues**: Report bugs at [GitHub Issues](https://github.com/Cornman92/DeployForge/issues)
- **Community**: GitHub Discussions for questions
- **In-App Tutorial**: Click "Quick Start Guide" on Welcome Page

### Reporting Issues

When reporting issues, include:

1. **DeployForge version**: Settings Page → About
2. **Windows version**: Output of `winver`
3. **Python version**: `python --version`
4. **Error logs**: Copy from log panel
5. **Steps to reproduce**: What you did before error occurred

### Feature Requests

Have an idea? Submit it at GitHub Discussions or Issues!

---

## Advanced Usage

### Custom Feature Profiles

Create your own reusable profiles:

1. Select features on Build Page
2. Click **"Save as Profile"** button
3. Name your profile (e.g., "Company Standard")
4. Profile appears in Profiles Page
5. Reuse anytime with one click!

### Configuration Export

Export your configuration for sharing:

1. After selecting features, click **"Export Config"**
2. Save as `config.json`
3. Share with colleagues
4. Others can **"Import Config"** and use your settings

### Automation (Advanced)

For power users, drive the GUI with scripts:

```python
from deployforge.gui_modern import MainWindow
from deployforge.cli.profiles import apply_profile

# Load profile programmatically
window = MainWindow()
apply_profile('gaming')  # Apply gaming profile
window.build_image()  # Start build
```

See `API_REFERENCE.md` for API automation.

---

## Frequently Asked Questions

### Q: Can I use DeployForge with Windows 10?

**A**: Yes! DeployForge supports Windows 10 and Windows 11 images.

### Q: Will this harm my Windows installation?

**A**: No. DeployForge modifies **offline images only**. Your running Windows is not affected.

### Q: Can I undo changes?

**A**: Original images are never modified. Work on copies. If build fails, no changes are made.

### Q: How long does a build take?

**A**: Depends on features selected and PC specs. Typical builds: 10-20 minutes.

### Q: Can I use this commercially?

**A**: Yes! MIT license. Free for personal and commercial use.

### Q: Do I need programming knowledge?

**A**: No! The GUI is designed for non-programmers. Point, click, customize!

### Q: Can I install my own applications?

**A**: Yes! Add custom applications in the Applications category or use the API.

### Q: Is internet required?

**A**: Only for downloading applications/drivers. Core functionality works offline.

---

## Conclusion

Congratulations! You're now ready to create custom Windows deployment images with DeployForge Modern GUI.

**Key Takeaways**:
- **150+ features** across 16 categories
- **6 pre-configured profiles** for quick setups
- **Drag-and-drop** image loading
- **Real-time progress** monitoring
- **Light & Dark themes**

**Next Steps**:
1. Launch DeployForge: `python -m deployforge.gui_modern`
2. Load a Windows image
3. Choose a profile or select features
4. Build your custom image!

**Happy Building!** 🚀

---

**Documentation Version**: 1.7.0
**Last Updated**: 2025-11-15
**Questions?**: https://github.com/Cornman92/DeployForge/discussions
