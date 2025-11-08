"""
Quick Setup Wizard Generator Module

Creates guided setup experience with presets.
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SetupPreset(Enum):
    """Setup presets"""
    GAMER = "gamer"
    DEVELOPER = "developer"
    CONTENT_CREATOR = "content-creator"
    STUDENT = "student"
    OFFICE = "office"


class SetupWizard:
    """Setup wizard generator"""

    PRESETS = {
        'gamer': {
            'name': 'Gaming Setup',
            'apps': ['Steam', 'Discord', 'MSI Afterburner'],
            'optimizations': ['gaming', 'performance'],
            'theme': 'dark'
        },
        'developer': {
            'name': 'Developer Setup',
            'apps': ['VS Code', 'Git', 'Python', 'Node.js'],
            'optimizations': ['performance'],
            'theme': 'dark'
        },
        'content-creator': {
            'name': 'Content Creator Setup',
            'apps': ['OBS Studio', 'GIMP', 'Audacity'],
            'optimizations': ['performance'],
            'theme': 'dark'
        }
    }

    def create_guided_setup(
        self,
        presets: List[str],
        output_path: Path
    ):
        """Create guided setup configuration"""
        config = {
            'version': '1.0',
            'presets': []
        }

        for preset in presets:
            if preset in self.PRESETS:
                config['presets'].append(self.PRESETS[preset])

        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Created setup wizard: {output_path}")


def create_quick_setup(preset: str = 'gamer') -> Dict[str, Any]:
    """Quick setup creation"""
    wizard = SetupWizard()
    return wizard.PRESETS.get(preset, wizard.PRESETS['gamer'])
