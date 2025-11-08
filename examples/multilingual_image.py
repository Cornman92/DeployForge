"""
DeployForge v0.3.0 Example: Multilingual Windows Image

This example demonstrates creating a Windows image with multi-language
support for global deployment.

Scenarios:
- European deployment (UK, Germany, France, Spain, Italy)
- Asian deployment (Japan, Korea, China)
- Custom language selection

Requirements:
- DeployForge 0.3.0 or later
- Windows install.wim image
- Language pack .cab files from Windows media or VLSC

Usage:
    python multilingual_image.py
"""

from pathlib import Path
from deployforge.languages import (
    LanguageManager,
    LanguageSettings,
    LanguageCode,
    create_multilingual_config,
    create_european_multilingual,
    create_asian_multilingual
)
import json


def create_european_office_image():
    """Create a multilingual image for European offices"""

    print("=" * 70)
    print("Scenario 1: European Office Deployment")
    print("=" * 70)
    print()

    # Configuration for European deployment
    config = create_european_multilingual()

    print("Configuration:")
    print(f"  Default Language: {config.default_language} (English UK)")
    print(f"  Installed Languages: {', '.join(config.installed_languages)}")
    print(f"  Time Zone: {config.time_zone}")
    print(f"  Keyboard Layouts: {len(config.keyboard_layouts)}")
    print()

    # Display language details
    print("Language Details:")
    language_names = {
        'en-GB': 'English (United Kingdom)',
        'de-DE': 'Deutsch (Germany)',
        'fr-FR': 'Français (France)',
        'es-ES': 'Español (Spain)',
        'it-IT': 'Italiano (Italy)'
    }

    for lang in config.installed_languages:
        tz = LanguageManager.get_recommended_timezone(lang)
        geo = LanguageManager.get_geo_id(lang)
        print(f"  • {language_names.get(lang, lang)}")
        print(f"      Time Zone: {tz}")
        print(f"      GeoID: {geo}")
    print()

    # Required language packs
    print("Required Language Packs:")
    print("  Download from:")
    print("  - Windows installation media (under sources)")
    print("  - Volume Licensing Service Center (VLSC)")
    print("  - Windows Update (for installed systems)")
    print()

    packs = [
        "Microsoft-Windows-Client-Language-Pack_x64_de-de.cab",
        "Microsoft-Windows-Client-Language-Pack_x64_fr-fr.cab",
        "Microsoft-Windows-Client-Language-Pack_x64_es-es.cab",
        "Microsoft-Windows-Client-Language-Pack_x64_it-it.cab"
    ]

    for pack in packs:
        print(f"  • {pack}")
    print()

    # Installation commands
    print("Installation Steps:")
    print()
    print("  1. Mount Windows image:")
    print("     dism /Mount-Wim /WimFile:install.wim /Index:1 /MountDir:C:\\mount")
    print()
    print("  2. Add each language pack:")
    for lang in ['de-de', 'fr-fr', 'es-es', 'it-it']:
        print(f"     dism /Image:C:\\mount /Add-Package "
              f"/PackagePath:Microsoft-Windows-Client-Language-Pack_x64_{lang}.cab")
    print()
    print("  3. Set default language (optional):")
    print(f"     dism /Image:C:\\mount /Set-AllIntl:{config.default_language}")
    print()
    print("  4. Unmount and save:")
    print("     dism /Unmount-Wim /MountDir:C:\\mount /Commit")
    print()

    # Save configuration
    config_path = Path("european_languages.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"✓ Configuration saved to {config_path}")
    print()


def create_asian_office_image():
    """Create a multilingual image for Asian offices"""

    print("=" * 70)
    print("Scenario 2: Asian Office Deployment")
    print("=" * 70)
    print()

    # Configuration for Asian deployment
    config = create_asian_multilingual()

    print("Configuration:")
    print(f"  Default Language: {config.default_language} (English US)")
    print(f"  Installed Languages: {', '.join(config.installed_languages)}")
    print(f"  Time Zone: {config.time_zone}")
    print(f"  Keyboard Layouts: {len(config.keyboard_layouts)}")
    print()

    # Display language details with native names
    print("Language Details:")
    language_names = {
        'en-US': 'English (United States)',
        'ja-JP': '日本語 (Japan)',
        'ko-KR': '한국어 (Korea)',
        'zh-CN': '中文简体 (China)',
        'zh-TW': '中文繁體 (Taiwan)'
    }

    for lang in config.installed_languages:
        tz = LanguageManager.get_recommended_timezone(lang)
        geo = LanguageManager.get_geo_id(lang)
        print(f"  • {language_names.get(lang, lang)}")
        print(f"      Time Zone: {tz}")
        print(f"      GeoID: {geo}")
    print()

    # Special considerations for Asian languages
    print("Special Considerations:")
    print("  • CJK (Chinese, Japanese, Korean) languages require:")
    print("    - Font packages (included in Windows)")
    print("    - IME (Input Method Editors) for text input")
    print("    - Regional standards (date formats, currency)")
    print()
    print("  • Default font rendering may need adjustment")
    print("  • Consider installing Office language packs separately")
    print()

    # Required language packs
    print("Required Language Packs:")
    packs = [
        "Microsoft-Windows-Client-Language-Pack_x64_ja-jp.cab",
        "Microsoft-Windows-Client-Language-Pack_x64_ko-kr.cab",
        "Microsoft-Windows-Client-Language-Pack_x64_zh-cn.cab",
        "Microsoft-Windows-Client-Language-Pack_x64_zh-tw.cab"
    ]

    for pack in packs:
        print(f"  • {pack}")
    print()

    # Save configuration
    config_path = Path("asian_languages.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"✓ Configuration saved to {config_path}")
    print()


def create_custom_global_image():
    """Create a custom multilingual image for global deployment"""

    print("=" * 70)
    print("Scenario 3: Custom Global Deployment")
    print("=" * 70)
    print()

    # Define custom language set
    languages = [
        LanguageCode.EN_US.value,  # English (US) - Default
        LanguageCode.EN_GB.value,  # English (UK)
        LanguageCode.DE_DE.value,  # German
        LanguageCode.FR_FR.value,  # French
        LanguageCode.ES_ES.value,  # Spanish (Spain)
        LanguageCode.ES_MX.value,  # Spanish (Mexico)
        LanguageCode.PT_BR.value,  # Portuguese (Brazil)
        LanguageCode.JA_JP.value,  # Japanese
        LanguageCode.ZH_CN.value,  # Chinese (Simplified)
        LanguageCode.AR_SA.value,  # Arabic
    ]

    config = create_multilingual_config(
        languages=languages,
        default_language=LanguageCode.EN_US.value
    )

    print("Configuration:")
    print(f"  Default Language: {config.default_language}")
    print(f"  Total Languages: {len(config.installed_languages)}")
    print(f"  Keyboard Layouts: {len(config.keyboard_layouts)}")
    print()

    print("Installed Languages:")
    for i, lang in enumerate(config.installed_languages, 1):
        tz = LanguageManager.get_recommended_timezone(lang)
        print(f"  {i:2}. {lang:8} - Time Zone: {tz}")
    print()

    # Deployment recommendations
    print("Deployment Recommendations:")
    print()
    print("  1. Image Size:")
    print("     • Each language pack: ~100-300 MB")
    print(f"     • Estimated total: ~{len(languages) * 200} MB additional")
    print("     • Consider separate images for different regions")
    print()
    print("  2. Update Strategy:")
    print("     • Language packs must match Windows build version")
    print("     • Update language packs when updating Windows")
    print("     • Test all languages after feature updates")
    print()
    print("  3. User Experience:")
    print("     • Users can change language in Settings > Time & Language")
    print("     • Changing UI language requires sign-out/sign-in")
    print("     • Some applications may need language-specific versions")
    print()
    print("  4. Licensing:")
    print("     • Windows 10/11 Pro/Enterprise includes all languages")
    print("     • Windows Home may have limitations")
    print("     • Verify licensing for your deployment")
    print()

    # Installation script
    print("Python Installation Script:")
    print()
    print("```python")
    print("from deployforge.languages import LanguageManager")
    print("from pathlib import Path")
    print()
    print("# Mount image")
    print("lm = LanguageManager(Path('install.wim'))")
    print("# (Requires external mounting: dism /Mount-Wim ...)")
    print()
    print("# Add each language pack")
    print("language_packs = [")
    for lang in languages[1:]:  # Skip en-US (already in base image)
        pack_name = f"Microsoft-Windows-Client-Language-Pack_x64_{lang.lower()}.cab"
        print(f"    Path('packs/{pack_name}'),")
    print("]")
    print()
    print("for pack in language_packs:")
    print("    lm.add_language_pack(pack)")
    print()
    print("# Set default language")
    print(f"lm.set_default_language('{config.default_language}')")
    print()
    print("# (Unmount with commit)")
    print("```")
    print()

    # Save configuration
    config_path = Path("global_languages.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"✓ Configuration saved to {config_path}")
    print()


def main():
    """Run all multilingual image scenarios"""

    print()
    print("DeployForge v0.3.0 - Multilingual Image Examples")
    print()

    # Scenario 1: European deployment
    create_european_office_image()

    # Scenario 2: Asian deployment
    create_asian_office_image()

    # Scenario 3: Custom global deployment
    create_custom_global_image()

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    print("Three multilingual configurations have been created:")
    print()
    print("  1. European: 5 languages (UK, DE, FR, ES, IT)")
    print("     File: european_languages.json")
    print()
    print("  2. Asian: 5 languages (US, JP, KR, CN, TW)")
    print("     File: asian_languages.json")
    print()
    print("  3. Global: 10 languages (worldwide coverage)")
    print("     File: global_languages.json")
    print()
    print("Next Steps:")
    print("  1. Download language packs from Microsoft")
    print("  2. Mount Windows image with DISM")
    print("  3. Apply language packs using DISM or DeployForge")
    print("  4. Set default language and regional settings")
    print("  5. Test language switching in OOBE and Settings")
    print()
    print("Tips:")
    print("  • Keep language packs version-matched with Windows")
    print("  • Test OOBE in each language")
    print("  • Document language support for end users")
    print("  • Consider automated testing for all languages")
    print()
    print("=" * 70)
    print("Multilingual image configurations complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
