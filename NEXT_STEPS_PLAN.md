# Next Steps Plan: Backend Feature Implementation & App Framework

**Goal**: Bridge the gap between the GUI (150+ features) and Backend Modules, and implement the Application Installer Framework.

## 1. Privacy & Security Hardening (`src/deployforge/privacy_hardening.py`)

**Current Status**: Configuration dataclass exists, but most flags are not implemented in `harden_privacy_settings`.
**Missing Implementations**:
- [ ] `disable_web_search` (Registry: HKCU\Software\Microsoft\Windows\CurrentVersion\Search)
- [ ] `disable_activity_history` (Registry: HKLM\SOFTWARE\Policies\Microsoft\Windows\System\PublishUserActivities)
- [ ] `disable_location_services` (Registry: HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location)
- [ ] `disable_feedback` (Registry: HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection\DoNotShowFeedbackNotifications)
- [ ] `disable_tailored_experiences` (Registry: HKCU\Software\Microsoft\Windows\CurrentVersion\Privacy\TailoredExperiencesWithDiagnosticDataEnabled)
- [ ] `disable_suggestions` (Registry: HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent)
- [ ] `disable_cloud_sync` (Registry: HKLM\SOFTWARE\Policies\Microsoft\Windows\SettingSync)
- [ ] `disable_wifi_sense` (Registry: HKLM\SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager)
- [ ] `disable_scheduled_tasks` (Schtasks /Change /Disable) for telemetry tasks.
- [ ] `harden_services` (Services: DiagTrack, dmwappushservice, etc.)

## 2. Application Installer Framework (`src/deployforge/applications.py`)

**Current Status**: Basic MSI/EXE injection. No native WinGet support.
**Implementation Plan**:
- [ ] Add `WinGet` support class/methods.
- [ ] Implement `install_winget_package(package_id, source, scope)`.
- [ ] Create PowerShell script generator for WinGet (similar to `devenv.py`).
- [ ] Add support for "Store Apps" via WinGet.
- [ ] Implement `ApplicationInjector.install_winget_app`.
- [ ] Add error handling for WinGet failures (internet access checks).

## 3. UI Customization (`src/deployforge/ui_customization.py`)

**Current Status**: Check if features like Taskbar alignment, Dark Mode, etc., are implemented.
**Implementation Plan**:
- [ ] Audit `ui_customization.py`.
- [ ] Implement missing visual tweaks (Taskbar, Start Menu, Explorer).

## 4. Execution Strategy

1.  **Refactor `privacy_hardening.py`**: Add missing methods and update main logic.
2.  **Enhance `applications.py`**: Add WinGet capabilities.
3.  **Refactor `ui_customization.py`**: Ensure visual features are backed by code.
4.  **Verify**: Run simple tests (or mock tests) to ensure methods are callable and generate correct registry/script outputs.
