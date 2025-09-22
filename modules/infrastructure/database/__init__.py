"""
WSP 78 Database Infrastructure Module

One Database, Three Namespaces:
- modules.*     # Module data
- foundups.*    # FoundUp projects
- agents.*      # Agent memory
"""

from .src import DatabaseManager, ModuleDB

__all__ = [
    'DatabaseManager',
    'ModuleDB'
]
