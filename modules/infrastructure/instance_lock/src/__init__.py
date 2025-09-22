"""
Instance Lock Module - Prevents duplicate process instances
"""

from .instance_manager import (
    InstanceLock,
    get_instance_lock,
    check_single_instance
)

__all__ = [
    'InstanceLock',
    'get_instance_lock',
    'check_single_instance'
]