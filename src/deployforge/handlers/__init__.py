"""Image format handlers for DeployForge."""

from deployforge.handlers.iso_handler import ISOHandler
from deployforge.handlers.wim_handler import WIMHandler
from deployforge.handlers.esd_handler import ESDHandler
from deployforge.handlers.ppkg_handler import PPKGHandler

# Register all handlers
from deployforge.core.image_manager import ImageManager

ImageManager.register_handler('.iso', ISOHandler)
ImageManager.register_handler('.wim', WIMHandler)
ImageManager.register_handler('.esd', ESDHandler)
ImageManager.register_handler('.ppkg', PPKGHandler)

__all__ = ['ISOHandler', 'WIMHandler', 'ESDHandler', 'PPKGHandler']
