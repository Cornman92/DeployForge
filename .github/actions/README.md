# DeployForge GitHub Actions

Automate Windows image customization with GitHub Actions.

## Quick Start

### Basic Usage

```yaml
name: Build Custom Image

on: [push]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Gaming Image
        uses: ./.github/actions/build-image
        with:
          image-path: './images/install.wim'
          profile: 'gamer'
          output-path: './custom.wim'
```

## Actions

### build-image

Build customized Windows deployment images.

**Inputs:**

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `image-path` | Yes | - | Path to source Windows image |
| `profile` | No | `gamer` | Profile to apply |
| `output-path` | No | `custom.wim` | Output image path |
| `preset` | No | - | Preset name (overrides profile) |
| `validate` | No | `true` | Validate after build |
| `generate-report` | No | `false` | Generate analysis report |
| `report-format` | No | `html` | Report format (text/json/html) |

**Outputs:**

| Output | Description |
|--------|-------------|
| `output-image` | Path to generated image |
| `validation-result` | Validation result (passed/failed) |
| `report-path` | Path to analysis report |

**Example:**

```yaml
- name: Build Image
  uses: ./.github/actions/build-image
  with:
    image-path: './install.wim'
    profile: 'developer'
    output-path: './developer.wim'
    validate: true
    generate-report: true
    report-format: 'html'
```

## Workflow Examples

### Example 1: Gaming Image Build

```yaml
name: Gaming Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Gaming Image
        uses: ./.github/actions/build-image
        with:
          image-path: './images/install.wim'
          profile: 'gamer'
          output-path: './gaming.wim'
          validate: true
          generate-report: true

      - name: Upload Image
        uses: actions/upload-artifact@v3
        with:
          name: gaming-image
          path: ./gaming.wim
```

### Example 2: Multi-Profile Build

```yaml
name: Multi-Profile Build

on: [workflow_dispatch]

jobs:
  build:
    runs-on: windows-latest
    strategy:
      matrix:
        profile: [gamer, developer, enterprise]

    steps:
      - uses: actions/checkout@v4

      - name: Build ${{ matrix.profile }} Image
        uses: ./.github/actions/build-image
        with:
          image-path: './images/install.wim'
          profile: ${{ matrix.profile }}
          output-path: './${{ matrix.profile }}.wim'

      - name: Upload
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.profile }}-image
          path: ./${{ matrix.profile }}.wim
```

### Example 3: Preset-Based Build

```yaml
name: Custom Preset Build

on:
  workflow_dispatch:
    inputs:
      preset-name:
        description: 'Preset to apply'
        required: true
        default: 'MyCustomGaming'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build with Preset
        uses: ./.github/actions/build-image
        with:
          image-path: './images/install.wim'
          preset: ${{ github.event.inputs.preset-name }}
          output-path: './custom.wim'
          validate: true
```

### Example 4: Validation Only

```yaml
name: Validate Image

on:
  pull_request:
    paths:
      - 'images/**'

jobs:
  validate:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install DeployForge
        run: pip install deployforge

      - name: Validate
        run: python -m deployforge.cli validate ./images/install.wim
```

### Example 5: Scheduled Builds

```yaml
name: Weekly Build

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Latest Image
        uses: ./.github/actions/build-image
        with:
          image-path: './images/install.wim'
          profile: 'gamer'
          output-path: './weekly-build.wim'
          generate-report: true

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: weekly-${{ github.run_number }}
          files: |
            ./weekly-build.wim
            deployforge-report.html
```

## Advanced Configuration

### Caching

Speed up builds with caching:

```yaml
- name: Cache Python Dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

- name: Install DeployForge
  run: pip install deployforge
```

### Artifacts

Upload build artifacts:

```yaml
- name: Upload Image
  uses: actions/upload-artifact@v3
  with:
    name: custom-image
    path: ./custom.wim
    retention-days: 30

- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: analysis-report
    path: deployforge-report.html
```

### Notifications

Send notifications on completion:

```yaml
- name: Notify Success
  if: success()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '✅ Image build completed successfully!'
      });
```

### Matrix Builds

Build multiple configurations:

```yaml
strategy:
  matrix:
    profile: [gamer, developer]
    arch: [x64, arm64]
    include:
      - profile: gamer
        preset: gaming-competitive
      - profile: developer
        preset: fullstack-dev
```

## Environment Variables

Configure DeployForge behavior:

```yaml
env:
  DEPLOYFORGE_LOG_LEVEL: DEBUG
  DEPLOYFORGE_TEMP_DIR: ./temp
```

## Secrets

Store sensitive data:

```yaml
- name: Download Private Image
  run: |
    curl -H "Authorization: Bearer ${{ secrets.IMAGE_TOKEN }}" \
      -o install.wim \
      ${{ secrets.IMAGE_URL }}
```

## Troubleshooting

### Python Not Found

```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
```

### DISM Errors

Ensure Windows runner:

```yaml
runs-on: windows-latest  # Required for DISM
```

### Timeout Issues

Increase timeout:

```yaml
- name: Build Image
  timeout-minutes: 60  # Increase for large images
  uses: ./.github/actions/build-image
```

## Best Practices

1. **Use Windows Runners**: DISM requires Windows
2. **Cache Dependencies**: Speed up builds
3. **Validate Images**: Always validate after customization
4. **Generate Reports**: Track changes with analysis reports
5. **Version Tags**: Tag releases with version numbers
6. **Artifact Retention**: Set appropriate retention periods
7. **Matrix Builds**: Build multiple profiles in parallel

## Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [DeployForge Documentation](https://github.com/YourOrg/DeployForge)
- [Example Workflows](https://github.com/YourOrg/DeployForge/tree/main/.github/workflows)
