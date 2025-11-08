# DeployForge for Visual Studio Code

Windows deployment image customization directly in VS Code.

## Features

- **Build Custom Images**: Apply profiles to Windows images with one click
- **Image Analysis**: Analyze image contents and generate detailed reports
- **Validation**: Validate image integrity and compatibility
- **Profile Management**: Quick access to all profiles
- **Preset System**: Create and apply custom presets
- **Image Comparison**: Compare two images side-by-side
- **Integrated UI**: Sidebar views for profiles, presets, and images

## Installation

1. Install the extension from VS Code Marketplace
2. Ensure Python 3.8+ is installed
3. Install DeployForge: `pip install deployforge`
4. Restart VS Code

## Quick Start

### Build an Image

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "DeployForge: Build Image"
3. Select source Windows image (.wim or .esd)
4. Choose a profile (gamer, developer, enterprise, etc.)
5. Select output location
6. Wait for build to complete

### Analyze an Image

1. Right-click a .wim file in Explorer
2. Select "DeployForge: Analyze Image"
3. View generated report

### Apply Profile

1. Right-click a .wim file
2. Select "DeployForge: Apply Profile"
3. Choose profile to apply

## Commands

| Command | Description |
|---------|-------------|
| `DeployForge: Build Image` | Build customized Windows image |
| `DeployForge: Analyze Image` | Analyze image and generate report |
| `DeployForge: Validate Image` | Validate image integrity |
| `DeployForge: Compare Images` | Compare two images |
| `DeployForge: Apply Profile` | Apply profile to image |
| `DeployForge: Create Preset` | Create new preset |
| `DeployForge: List Profiles` | Show available profiles |
| `DeployForge: List Presets` | Show available presets |
| `DeployForge: Open Report` | Open analysis report |

## Profiles

### Gaming Profile
- Performance optimizations
- Gaming launchers (Steam, Epic, GOG)
- Network latency tweaks
- Bloatware removed
- Dark theme

### Developer Profile
- WSL2 enabled
- Hyper-V enabled
- Development tools (Git, VS Code, Docker)
- Programming languages
- Developer Mode enabled

### Enterprise Profile
- Security hardening
- BitLocker configuration
- Group Policy settings
- Certificate management
- Enterprise applications

### Student Profile
- Productivity tools
- Microsoft Office
- Educational software
- Balanced performance

### Creator Profile
- Creative tools (OBS, GIMP, Audacity, Blender)
- Performance optimizations
- Media codecs
- Storage optimization

## Sidebar Views

### Profiles View
- Browse available profiles
- Click to apply to an image
- View profile descriptions

### Presets View
- Browse custom presets
- Create new presets
- Apply presets to images

### Images View
- Recent images in workspace
- Quick access to common operations
- Image metadata display

## Context Menus

Right-click on .wim or .esd files in Explorer:
- Analyze Image
- Validate Image
- Apply Profile

## Configuration

Configure DeployForge in VS Code settings:

```json
{
  "deployforge.pythonPath": "python",
  "deployforge.defaultProfile": "gamer",
  "deployforge.autoValidate": true,
  "deployforge.generateReports": true,
  "deployforge.reportFormat": "html",
  "deployforge.showNotifications": true
}
```

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `deployforge.pythonPath` | string | `python` | Path to Python executable |
| `deployforge.defaultProfile` | string | `gamer` | Default profile for builds |
| `deployforge.autoValidate` | boolean | `true` | Auto-validate after build |
| `deployforge.generateReports` | boolean | `true` | Auto-generate reports |
| `deployforge.reportFormat` | string | `html` | Report format (text/json/html) |
| `deployforge.showNotifications` | boolean | `true` | Show notifications |

## Examples

### Example 1: Build Gaming Image

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run `DeployForge: Build Image`
3. Select `install.wim`
4. Choose `gamer` profile
5. Save as `gaming.wim`

### Example 2: Analyze Image

1. Find .wim file in Explorer
2. Right-click → "DeployForge: Analyze Image"
3. View HTML report in browser

### Example 3: Compare Images

1. Run `DeployForge: Compare Images`
2. Select first image (original)
3. Select second image (customized)
4. View differences in Output panel

### Example 4: Create Custom Preset

1. Run `DeployForge: Create Preset`
2. Enter name: "My Gaming Setup"
3. Choose base profile: `gamer`
4. Preset saved for reuse

## Keyboard Shortcuts

No default shortcuts. Add your own in Keyboard Shortcuts settings:

```json
{
  "key": "ctrl+alt+b",
  "command": "deployforge.buildImage"
}
```

## Tasks Integration

Create a `tasks.json` file:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build Gaming Image",
      "type": "deployforge",
      "command": "build",
      "args": [
        "--profile", "gamer",
        "--output", "gaming.wim"
      ],
      "problemMatcher": []
    }
  ]
}
```

## Snippets

Use snippets in JSON/YAML preset files:

Type `df-preset` for preset template:

```json
{
  "name": "My Preset",
  "description": "Custom preset",
  "actions": [
    {
      "module": "gaming",
      "action": "apply_profile",
      "parameters": {
        "profile": "competitive"
      }
    }
  ]
}
```

## Troubleshooting

### Extension Not Activating

1. Check Python is installed: `python --version`
2. Check DeployForge is installed: `pip show deployforge`
3. Restart VS Code
4. Check Output panel for errors

### Commands Not Working

1. Verify Python path in settings
2. Ensure DISM is available (Windows only)
3. Run VS Code as Administrator for DISM operations
4. Check extension logs in Output panel

### Build Failures

1. Verify source image is valid
2. Check disk space
3. Ensure no other process is using the image
4. Run validation on source image first

## Tips & Tricks

### Batch Processing

Create a task to process multiple images:

```json
{
  "label": "Build All Profiles",
  "type": "shell",
  "command": "python -m deployforge.cli build ${file} --profile gamer && python -m deployforge.cli build ${file} --profile developer"
}
```

### Auto-Validation

Enable automatic validation in settings:

```json
{
  "deployforge.autoValidate": true
}
```

### Custom Reports

Generate reports automatically:

```json
{
  "deployforge.generateReports": true,
  "deployforge.reportFormat": "html"
}
```

## Requirements

- Visual Studio Code 1.80.0 or later
- Python 3.8 or later
- DeployForge Python package
- Windows 10/11 with DISM (for image operations)

## Extension Development

### Setup

```bash
cd vscode-extension
npm install
npm run compile
```

### Testing

```bash
npm run test
```

### Debugging

1. Open `vscode-extension` folder in VS Code
2. Press F5 to launch Extension Development Host
3. Test commands in new window

### Publishing

```bash
npm install -g @vscode/vsce
vsce package
vsce publish
```

## Contributing

Contributions welcome! Please see main repository for guidelines.

## License

See LICENSE file in main repository.

## Links

- [DeployForge Repository](https://github.com/YourOrg/DeployForge)
- [Documentation](https://github.com/YourOrg/DeployForge/wiki)
- [Issue Tracker](https://github.com/YourOrg/DeployForge/issues)
- [VS Code Extension API](https://code.visualstudio.com/api)

## Release Notes

### 0.6.0

- Initial release
- Build, analyze, and validate images
- Profile and preset management
- Sidebar views
- Context menu integration
- Task support
- Configuration options

---

**Enjoy customizing Windows images in VS Code!**
