"""Adapters for bridging simulator to FAM modules.

These are THIN wrappers - NO logic invention.
"""

from .fam_bridge import FAMBridge
from .phantom_plugs import PhantomTokenEconomy, PhantomSocialActions

__all__ = ["FAMBridge", "PhantomTokenEconomy", "PhantomSocialActions"]
