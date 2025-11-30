"""
Multi-Language Support (MUI) for DeployForge

This module provides functionality for managing Windows Multilingual User Interface (MUI)
packages, also known as Language Packs or Language Interface Packs.

Features:
- Language pack installation and removal
- Language Interface Pack (LIP) support
- Default language configuration
- Regional settings management
- Keyboard layout configuration
- Language-specific features and components
- Bulk language management

Platform Support:
- Windows: DISM with language pack management
- Linux: Limited support via wimlib
"""

import json
import logging
import platform
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

logger = logging.getLogger(__name__)


class LanguageCode(Enum):
    """Common Windows language codes (BCP-47 format)"""

    # Western Europe
    EN_US = "en-US"  # English (United States)
    EN_GB = "en-GB"  # English (United Kingdom)
    DE_DE = "de-DE"  # German
    FR_FR = "fr-FR"  # French
    ES_ES = "es-ES"  # Spanish (Spain)
    ES_MX = "es-MX"  # Spanish (Mexico)
    IT_IT = "it-IT"  # Italian
    PT_PT = "pt-PT"  # Portuguese (Portugal)
    PT_BR = "pt-BR"  # Portuguese (Brazil)
    NL_NL = "nl-NL"  # Dutch

    # Eastern Europe
    PL_PL = "pl-PL"  # Polish
    RU_RU = "ru-RU"  # Russian
    CS_CZ = "cs-CZ"  # Czech
    HU_HU = "hu-HU"  # Hungarian
    RO_RO = "ro-RO"  # Romanian
    BG_BG = "bg-BG"  # Bulgarian
    UK_UA = "uk-UA"  # Ukrainian

    # Nordic
    SV_SE = "sv-SE"  # Swedish
    NO_NO = "no-NO"  # Norwegian
    DA_DK = "da-DK"  # Danish
    FI_FI = "fi-FI"  # Finnish

    # Asia
    ZH_CN = "zh-CN"  # Chinese (Simplified)
    ZH_TW = "zh-TW"  # Chinese (Traditional)
    JA_JP = "ja-JP"  # Japanese
    KO_KR = "ko-KR"  # Korean
    TH_TH = "th-TH"  # Thai
    VI_VN = "vi-VN"  # Vietnamese
    HI_IN = "hi-IN"  # Hindi

    # Middle East
    AR_SA = "ar-SA"  # Arabic
    HE_IL = "he-IL"  # Hebrew
    TR_TR = "tr-TR"  # Turkish
    FA_IR = "fa-IR"  # Persian


class LanguagePackType(Enum):
    """Types of language packs"""

    FULL = "Full"  # Complete language pack
    PARTIAL = "Partial"  # Partial language pack (some components)
    LIP = "LIP"  # Language Interface Pack
    FEATURES_ON_DEMAND = "FOD"  # Features on Demand


class KeyboardLayout(Enum):
    """Common keyboard layouts (input locales)"""

    # US/UK
    US_QWERTY = "0409:00000409"
    UK_QWERTY = "0809:00000809"

    # European
    GERMAN = "0407:00000407"
    FRENCH = "040c:0000040c"
    SPANISH = "0c0a:0000040a"
    ITALIAN = "0410:00000410"

    # Asian
    JAPANESE = "0411:00000411"
    KOREAN = "0412:00000412"
    CHINESE_SIMPLIFIED = "0804:00000804"
    CHINESE_TRADITIONAL = "0404:00000404"


@dataclass
class LanguagePack:
    """Represents an installed or available language pack"""

    language: str
    display_name: str
    type: LanguagePackType
    package_path: Optional[Path] = None
    is_installed: bool = False
    is_default: bool = False
    features: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "language": self.language,
            "display_name": self.display_name,
            "type": self.type.value,
            "package_path": str(self.package_path) if self.package_path else None,
            "is_installed": self.is_installed,
            "is_default": self.is_default,
            "features": self.features,
        }


@dataclass
class LanguageSettings:
    """Complete language configuration"""

    default_language: str = "en-US"
    fallback_language: str = "en-US"
    installed_languages: List[str] = field(default_factory=list)
    keyboard_layouts: List[str] = field(default_factory=list)
    time_zone: str = "Pacific Standard Time"
    location: str = "244"  # United States

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "default_language": self.default_language,
            "fallback_language": self.fallback_language,
            "installed_languages": self.installed_languages,
            "keyboard_layouts": self.keyboard_layouts,
            "time_zone": self.time_zone,
            "location": self.location,
        }


class LanguageManager:
    """Manages language packs in Windows images"""

    # Time zone mappings
    TIME_ZONES = {
        "en-US": "Pacific Standard Time",
        "en-GB": "GMT Standard Time",
        "de-DE": "W. Europe Standard Time",
        "fr-FR": "Romance Standard Time",
        "es-ES": "Romance Standard Time",
        "it-IT": "W. Europe Standard Time",
        "ja-JP": "Tokyo Standard Time",
        "ko-KR": "Korea Standard Time",
        "zh-CN": "China Standard Time",
        "zh-TW": "Taipei Standard Time",
        "ru-RU": "Russian Standard Time",
        "ar-SA": "Arab Standard Time",
    }

    # GeoID mappings (location codes)
    GEO_IDS = {
        "en-US": "244",  # United States
        "en-GB": "242",  # United Kingdom
        "de-DE": "94",  # Germany
        "fr-FR": "84",  # France
        "es-ES": "217",  # Spain
        "it-IT": "118",  # Italy
        "ja-JP": "122",  # Japan
        "ko-KR": "134",  # Korea
        "zh-CN": "45",  # China
        "zh-TW": "237",  # Taiwan
    }

    def __init__(self, image_path: Path):
        """
        Initialize language manager

        Args:
            image_path: Path to Windows image (WIM/ISO)
        """
        self.image_path = image_path
        self.platform = platform.system()
        self.mount_point: Optional[Path] = None
        self.installed_packs: List[LanguagePack] = []

    def get_installed_languages(self) -> List[LanguagePack]:
        """
        Get list of installed language packs

        Returns:
            List of installed LanguagePack objects
        """
        if not self.mount_point:
            raise RuntimeError("Image must be mounted first")

        logger.info("Querying installed language packs")

        if self.platform == "Windows":
            return self._get_languages_windows()
        else:
            return self._get_languages_linux()

    def _get_languages_windows(self) -> List[LanguagePack]:
        """Get installed languages using DISM on Windows"""
        packs = []

        try:
            result = subprocess.run(
                ["dism", f"/Image:{self.mount_point}", "/Get-Intl"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse DISM output
            current_lang = None
            for line in result.stdout.split("\n"):
                line = line.strip()

                if "Default system UI language" in line:
                    current_lang = line.split(":")[-1].strip()

                elif "Installed language(s)" in line:
                    # Next lines contain installed languages
                    continue

                elif line and current_lang:
                    # Language code line
                    if len(line.split()) == 1 and "-" in line:
                        pack = LanguagePack(
                            language=line,
                            display_name=self._get_language_display_name(line),
                            type=LanguagePackType.FULL,
                            is_installed=True,
                            is_default=(line == current_lang),
                        )
                        packs.append(pack)

        except Exception as e:
            logger.error(f"Failed to query languages: {e}")

        self.installed_packs = packs
        return packs

    def _get_languages_linux(self) -> List[LanguagePack]:
        """Get installed languages on Linux (limited support)"""
        logger.warning("Language detection on Linux is limited")
        return []

    def _get_language_display_name(self, language_code: str) -> str:
        """Get display name for language code"""
        # Simplified mapping
        names = {
            "en-US": "English (United States)",
            "en-GB": "English (United Kingdom)",
            "de-DE": "Deutsch (Deutschland)",
            "fr-FR": "Français (France)",
            "es-ES": "Español (España)",
            "it-IT": "Italiano (Italia)",
            "ja-JP": "日本語 (日本)",
            "ko-KR": "한국어 (대한민국)",
            "zh-CN": "中文(简体)",
            "zh-TW": "中文(繁體)",
            "pt-BR": "Português (Brasil)",
            "ru-RU": "Русский (Россия)",
        }

        return names.get(language_code, language_code)

    def add_language_pack(self, language_pack_path: Path, language_code: Optional[str] = None):
        """
        Install language pack to image

        Args:
            language_pack_path: Path to .cab language pack file
            language_code: Language code (auto-detected if None)
        """
        if not self.mount_point:
            raise RuntimeError("Image must be mounted first")

        if not language_pack_path.exists():
            raise FileNotFoundError(f"Language pack not found: {language_pack_path}")

        logger.info(f"Installing language pack: {language_pack_path}")

        if self.platform == "Windows":
            subprocess.run(
                [
                    "dism",
                    f"/Image:{self.mount_point}",
                    "/Add-Package",
                    f"/PackagePath:{language_pack_path}",
                ],
                check=True,
                timeout=600,
            )

            logger.info(f"Language pack installed: {language_pack_path}")

        else:
            logger.warning("Language pack installation on Linux is not supported")

    def remove_language_pack(self, language_code: str):
        """
        Remove language pack from image

        Args:
            language_code: Language code to remove (e.g., 'fr-FR')
        """
        if not self.mount_point:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Removing language pack: {language_code}")

        if self.platform == "Windows":
            # Get package identity first
            result = subprocess.run(
                ["dism", f"/Image:{self.mount_point}", "/Get-Packages"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Find language pack package identity
            package_identity = None
            for line in result.stdout.split("\n"):
                if (
                    f"Language.Basic~~~{language_code}" in line
                    or f"LanguagePack-{language_code}" in line.lower()
                ):
                    # Extract package identity
                    if "Package Identity" in line:
                        package_identity = line.split(":")[-1].strip()
                        break

            if package_identity:
                subprocess.run(
                    [
                        "dism",
                        f"/Image:{self.mount_point}",
                        "/Remove-Package",
                        f"/PackageName:{package_identity}",
                    ],
                    check=True,
                    timeout=600,
                )

                logger.info(f"Language pack removed: {language_code}")
            else:
                logger.warning(f"Language pack not found: {language_code}")

        else:
            logger.warning("Language pack removal on Linux is not supported")

    def set_default_language(self, language_code: str):
        """
        Set default system language

        Args:
            language_code: Language code (e.g., 'en-US')
        """
        if not self.mount_point:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Setting default language: {language_code}")

        if self.platform == "Windows":
            subprocess.run(
                ["dism", f"/Image:{self.mount_point}", "/Set-AllIntl:{language_code}"],
                check=True,
                timeout=120,
            )

            logger.info(f"Default language set to: {language_code}")

        else:
            logger.warning("Setting default language on Linux is not supported")

    def set_ui_language(self, language_code: str):
        """
        Set UI language only (not system locale)

        Args:
            language_code: Language code
        """
        if not self.mount_point:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Setting UI language: {language_code}")

        if self.platform == "Windows":
            subprocess.run(
                ["dism", f"/Image:{self.mount_point}", f"/Set-UILang:{language_code}"],
                check=True,
                timeout=120,
            )

        else:
            logger.warning("Setting UI language on Linux is not supported")

    def set_input_locale(self, locale: str):
        """
        Set keyboard input locale

        Args:
            locale: Input locale code (e.g., '0409:00000409' for US)
        """
        if not self.mount_point:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Setting input locale: {locale}")

        if self.platform == "Windows":
            subprocess.run(
                ["dism", f"/Image:{self.mount_point}", f"/Set-InputLocale:{locale}"],
                check=True,
                timeout=120,
            )

        else:
            logger.warning("Setting input locale on Linux is not supported")

    def set_timezone(self, timezone: str):
        """
        Set time zone

        Args:
            timezone: Time zone name (e.g., 'Pacific Standard Time')
        """
        if not self.mount_point:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Setting time zone: {timezone}")

        if self.platform == "Windows":
            subprocess.run(
                ["dism", f"/Image:{self.mount_point}", f"/Set-TimeZone:{timezone}"],
                check=True,
                timeout=120,
            )

        else:
            logger.warning("Setting time zone on Linux is not supported")

    def apply_language_settings(self, settings: LanguageSettings):
        """
        Apply complete language configuration

        Args:
            settings: LanguageSettings object
        """
        if not self.mount_point:
            raise RuntimeError("Image must be mounted first")

        logger.info("Applying language settings")

        # Set all international settings at once
        if self.platform == "Windows":
            subprocess.run(
                ["dism", f"/Image:{self.mount_point}", f"/Set-AllIntl:{settings.default_language}"],
                check=True,
                timeout=120,
            )

            # Set time zone
            if settings.time_zone:
                self.set_timezone(settings.time_zone)

            # Set keyboard layouts
            if settings.keyboard_layouts:
                for layout in settings.keyboard_layouts:
                    self.set_input_locale(layout)

            logger.info("Language settings applied successfully")

        else:
            logger.warning("Applying language settings on Linux is not supported")

    def install_multiple_languages(
        self, language_packs: List[Path], default_language: Optional[str] = None
    ):
        """
        Install multiple language packs at once

        Args:
            language_packs: List of language pack .cab files
            default_language: Default language code (optional)
        """
        logger.info(f"Installing {len(language_packs)} language packs")

        for pack_path in language_packs:
            try:
                self.add_language_pack(pack_path)
            except Exception as e:
                logger.error(f"Failed to install {pack_path}: {e}")
                continue

        if default_language:
            self.set_default_language(default_language)

        logger.info("Multiple language installation complete")

    def export_language_config(self, output_path: Path):
        """
        Export current language configuration to JSON

        Args:
            output_path: Output JSON file path
        """
        packs = self.get_installed_languages()

        config = {
            "installed_languages": [p.to_dict() for p in packs],
            "default_language": next((p.language for p in packs if p.is_default), None),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"Language configuration exported to {output_path}")

    def import_language_config(self, config_path: Path) -> LanguageSettings:
        """
        Import language configuration from JSON

        Args:
            config_path: Path to configuration JSON

        Returns:
            LanguageSettings object
        """
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        settings = LanguageSettings(
            default_language=config.get("default_language", "en-US"),
            installed_languages=config.get("installed_languages", []),
            keyboard_layouts=config.get("keyboard_layouts", []),
            time_zone=config.get("time_zone", "Pacific Standard Time"),
            location=config.get("location", "244"),
        )

        logger.info(f"Language configuration imported from {config_path}")

        return settings

    @staticmethod
    def get_recommended_timezone(language_code: str) -> str:
        """
        Get recommended time zone for language code

        Args:
            language_code: Language code

        Returns:
            Time zone name
        """
        return LanguageManager.TIME_ZONES.get(language_code, "Pacific Standard Time")

    @staticmethod
    def get_geo_id(language_code: str) -> str:
        """
        Get geographic location ID for language code

        Args:
            language_code: Language code

        Returns:
            GeoID string
        """
        return LanguageManager.GEO_IDS.get(language_code, "244")


def create_multilingual_config(
    languages: List[str], default_language: str = "en-US"
) -> LanguageSettings:
    """
    Create multi-language configuration

    Args:
        languages: List of language codes to install
        default_language: Default language

    Returns:
        LanguageSettings object
    """
    settings = LanguageSettings(
        default_language=default_language, fallback_language="en-US", installed_languages=languages
    )

    # Set time zone based on default language
    settings.time_zone = LanguageManager.get_recommended_timezone(default_language)
    settings.location = LanguageManager.get_geo_id(default_language)

    # Add keyboard layouts for all languages
    for lang in languages:
        # Simplified keyboard layout mapping
        layout_map = {
            "en-US": "0409:00000409",
            "en-GB": "0809:00000809",
            "de-DE": "0407:00000407",
            "fr-FR": "040c:0000040c",
            "es-ES": "0c0a:0000040a",
            "ja-JP": "0411:00000411",
            "ko-KR": "0412:00000412",
            "zh-CN": "0804:00000804",
        }

        layout = layout_map.get(lang)
        if layout and layout not in settings.keyboard_layouts:
            settings.keyboard_layouts.append(layout)

    return settings


def create_european_multilingual() -> LanguageSettings:
    """
    Create European multi-language configuration

    Returns:
        LanguageSettings with common European languages
    """
    return create_multilingual_config(
        languages=["en-GB", "de-DE", "fr-FR", "es-ES", "it-IT"], default_language="en-GB"
    )


def create_asian_multilingual() -> LanguageSettings:
    """
    Create Asian multi-language configuration

    Returns:
        LanguageSettings with common Asian languages
    """
    return create_multilingual_config(
        languages=["en-US", "ja-JP", "ko-KR", "zh-CN", "zh-TW"], default_language="en-US"
    )
