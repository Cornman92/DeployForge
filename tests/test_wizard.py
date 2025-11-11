"""Unit Tests for Setup Wizard Module"""

import pytest
from pathlib import Path
from deployforge.wizard import (
    SetupWizard,
    SetupPreset,
    WizardConfig,
    create_quick_setup
)


class TestWizardConfig:
    def test_default_config(self):
        config = WizardConfig()
        assert config.preset_name == "Custom Setup"
        assert config.min_ram_gb == 8

    def test_to_dict(self):
        config = WizardConfig(
            preset_name="Gaming",
            essential_apps=["Steam", "Discord"]
        )
        config_dict = config.to_dict()
        assert config_dict['preset']['name'] == "Gaming"
        assert "Steam" in config_dict['applications']['essential']


class TestSetupWizard:
    def test_initialization(self):
        wizard = SetupWizard()
        assert isinstance(wizard.config, WizardConfig)

    def test_get_gaming_preset(self):
        wizard = SetupWizard()
        config = wizard.get_preset(SetupPreset.GAMING)
        assert config.preset_name == "Gaming Setup"
        assert "Steam" in config.essential_apps

    def test_recommend_preset(self):
        wizard = SetupWizard()
        preset = wizard.recommend_preset("I'm a gamer")
        assert preset == SetupPreset.GAMING
