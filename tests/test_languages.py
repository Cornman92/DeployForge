"""
Tests for multi-language support
"""

import pytest
from pathlib import Path
from deployforge.languages import (
    LanguageManager,
    LanguagePack,
    LanguageSettings,
    LanguagePackType,
    LanguageCode,
    create_multilingual_config,
    create_european_multilingual,
    create_asian_multilingual
)


def test_language_pack_creation():
    """Test creating a language pack"""
    pack = LanguagePack(
        language="en-US",
        display_name="English (United States)",
        type=LanguagePackType.FULL,
        is_installed=True,
        is_default=True
    )

    assert pack.language == "en-US"
    assert pack.display_name == "English (United States)"
    assert pack.is_installed is True
    assert pack.is_default is True

    data = pack.to_dict()
    assert data['language'] == "en-US"
    assert data['type'] == "Full"


def test_language_settings():
    """Test language settings"""
    settings = LanguageSettings(
        default_language="en-US",
        fallback_language="en-US",
        installed_languages=["en-US", "de-DE", "fr-FR"],
        time_zone="Pacific Standard Time"
    )

    assert settings.default_language == "en-US"
    assert len(settings.installed_languages) == 3
    assert "de-DE" in settings.installed_languages

    data = settings.to_dict()
    assert data['default_language'] == "en-US"
    assert len(data['installed_languages']) == 3


def test_multilingual_config_creation():
    """Test creating multilingual configuration"""
    config = create_multilingual_config(
        languages=["en-US", "de-DE", "fr-FR", "es-ES"],
        default_language="en-US"
    )

    assert config.default_language == "en-US"
    assert config.fallback_language == "en-US"
    assert len(config.installed_languages) == 4
    assert "de-DE" in config.installed_languages


def test_european_multilingual_config():
    """Test European multilingual configuration"""
    config = create_european_multilingual()

    assert config.default_language == "en-GB"
    assert "de-DE" in config.installed_languages
    assert "fr-FR" in config.installed_languages
    assert "es-ES" in config.installed_languages
    assert "it-IT" in config.installed_languages


def test_asian_multilingual_config():
    """Test Asian multilingual configuration"""
    config = create_asian_multilingual()

    assert config.default_language == "en-US"
    assert "ja-JP" in config.installed_languages
    assert "ko-KR" in config.installed_languages
    assert "zh-CN" in config.installed_languages
    assert "zh-TW" in config.installed_languages


def test_language_manager_timezone_mapping():
    """Test recommended timezone mapping"""
    assert LanguageManager.get_recommended_timezone("en-US") == "Pacific Standard Time"
    assert LanguageManager.get_recommended_timezone("de-DE") == "W. Europe Standard Time"
    assert LanguageManager.get_recommended_timezone("ja-JP") == "Tokyo Standard Time"


def test_language_manager_geo_id_mapping():
    """Test GeoID mapping"""
    assert LanguageManager.get_geo_id("en-US") == "244"  # United States
    assert LanguageManager.get_geo_id("de-DE") == "94"   # Germany
    assert LanguageManager.get_geo_id("ja-JP") == "122"  # Japan


def test_language_code_enum():
    """Test LanguageCode enum"""
    assert LanguageCode.EN_US.value == "en-US"
    assert LanguageCode.DE_DE.value == "de-DE"
    assert LanguageCode.FR_FR.value == "fr-FR"
    assert LanguageCode.JA_JP.value == "ja-JP"


def test_language_pack_type_enum():
    """Test LanguagePackType enum"""
    assert LanguagePackType.FULL.value == "Full"
    assert LanguagePackType.PARTIAL.value == "Partial"
    assert LanguagePackType.LIP.value == "LIP"


def test_language_settings_keyboard_layouts():
    """Test keyboard layout configuration"""
    settings = LanguageSettings(
        default_language="en-US",
        keyboard_layouts=["0409:00000409", "0407:00000407"]
    )

    assert len(settings.keyboard_layouts) == 2
    assert "0409:00000409" in settings.keyboard_layouts  # US
    assert "0407:00000407" in settings.keyboard_layouts  # German


def test_multilingual_config_with_keyboards():
    """Test multilingual config includes keyboard layouts"""
    config = create_multilingual_config(
        languages=["en-US", "de-DE", "fr-FR"],
        default_language="en-US"
    )

    # Should automatically add keyboard layouts
    assert len(config.keyboard_layouts) >= 1


def test_language_pack_features():
    """Test language pack features list"""
    pack = LanguagePack(
        language="en-US",
        display_name="English",
        type=LanguagePackType.FULL,
        features=["Handwriting", "OCR", "Speech"]
    )

    assert len(pack.features) == 3
    assert "Handwriting" in pack.features


def test_language_settings_location():
    """Test location (GeoID) setting"""
    settings = LanguageSettings(
        default_language="de-DE",
        location="94"  # Germany
    )

    assert settings.location == "94"


def test_language_manager_creation(tmp_path):
    """Test creating language manager"""
    image_path = tmp_path / "test.wim"

    lm = LanguageManager(image_path)

    assert lm.image_path == image_path
    assert lm.mount_point is None


def test_export_language_config(tmp_path):
    """Test exporting language configuration"""
    # Would require mounted image in real scenario
    # This is a basic structure test

    settings = LanguageSettings(
        default_language="en-US",
        installed_languages=["en-US", "de-DE"],
        keyboard_layouts=["0409:00000409"]
    )

    data = settings.to_dict()

    assert 'default_language' in data
    assert 'installed_languages' in data
    assert len(data['installed_languages']) == 2
