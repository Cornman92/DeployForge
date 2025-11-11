"""Unit Tests for Backup Module"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from deployforge.backup import (
    BackupIntegrator,
    BackupProfile,
    BackupType,
    RecoveryMode,
    BackupConfig,
    configure_backup
)


class TestBackupConfig:
    def test_default_config(self):
        config = BackupConfig()
        assert config.enable_system_restore is True
        assert config.enable_vss is True

    def test_to_dict(self):
        config = BackupConfig()
        config_dict = config.to_dict()
        assert 'system_restore' in config_dict
        assert 'vss' in config_dict
        assert 'recovery' in config_dict


class TestBackupIntegrator:
    def test_initialization(self, test_image_path):
        integrator = BackupIntegrator(test_image_path)
        assert integrator.image_path == test_image_path
        assert isinstance(integrator.config, BackupConfig)

    @patch('subprocess.run')
    def test_apply_aggressive_profile(self, mock_run, test_image_path, test_mount_point):
        integrator = BackupIntegrator(test_image_path)
        integrator._mounted = True
        integrator.mount_point = test_mount_point
        mock_run.return_value = Mock(returncode=0)

        integrator.apply_profile(BackupProfile.AGGRESSIVE)

        assert integrator.config.enable_system_restore is True
        assert integrator.config.enable_vss is True
        assert integrator.config.file_history_frequency == 30
