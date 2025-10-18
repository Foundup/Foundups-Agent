# -*- coding: utf-8 -*-
"""
Secrets MCP Server Implementation
Secure environment variable and .env file access for 0102 agents.

WSP Compliance: WSP 77, WSP 90
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

# Apply WSP 90 UTF-8 enforcement
if sys.platform.startswith('win'):
    # Safe UTF-8 wrapper to prevent UnicodeEncodeError
    class SafeUTF8Wrapper:
        def __init__(self, original_stream):
            self.original_stream = original_stream
            self.encoding = 'utf-8'
            self.errors = 'replace'

        def write(self, data):
            try:
                if isinstance(data, str):
                    encoded = data.encode('utf-8', errors='replace')
                    if hasattr(self.original_stream, 'buffer'):
                        self.original_stream.buffer.write(encoded)
                    else:
                        self.original_stream.write(data.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
                else:
                    self.original_stream.write(data)
            except Exception:
                try:
                    self.original_stream.write(str(data))
                except Exception:
                    pass

        def flush(self):
            try:
                self.original_stream.flush()
            except Exception:
                pass

        def __getattr__(self, name):
            return getattr(self.original_stream, name)

    if not isinstance(sys.stdout, SafeUTF8Wrapper):
        sys.stdout = SafeUTF8Wrapper(sys.stdout)
    if not isinstance(sys.stderr, SafeUTF8Wrapper):
        sys.stderr = SafeUTF8Wrapper(sys.stderr)


class SecretsMCPServer:
    """Secure MCP server for environment variable and .env file access"""

    def __init__(self):
        # Security filters - these patterns will be blocked
        self.sensitive_patterns = [
            r'password|pwd|secret|key|token|auth',
            r'api.*key|access.*key|secret.*key',
            r'database.*url|db.*url|connection.*string',
            r'private.*key|ssl.*key|certificate',
            r'credential|login|username|user',
            r'salt|hash|encrypt'
        ]

        # Allowed environment variable prefixes (whitelist approach)
        self.allowed_prefixes = [
            'PYTHON', 'PATH', 'HOME', 'USER', 'SHELL', 'TERM',
            'FOUNDUPS', 'WSP', 'MCP', 'HOLO', 'GIT',
            'LANG', 'LC_', 'TZ', 'HOSTNAME'
        ]

        # Restricted file paths (prevent access to sensitive directories)
        self.restricted_paths = [
            '/etc', '/root', '/home', '/usr/local',
            'C:\\Windows', 'C:\\Program Files', 'C:\\Users'
        ]

    def _is_sensitive(self, key: str, value: str = "") -> bool:
        """Check if an environment variable is sensitive"""
        key_lower = key.lower()
        value_lower = value.lower()

        # Check key patterns
        for pattern in self.sensitive_patterns:
            if re.search(pattern, key_lower, re.IGNORECASE):
                return True

        # Check value patterns (first 50 chars to avoid large values)
        value_preview = value_lower[:50]
        for pattern in self.sensitive_patterns:
            if re.search(pattern, value_preview, re.IGNORECASE):
                return True

        return False

    def _is_allowed_env_var(self, key: str) -> bool:
        """Check if environment variable is allowed to be accessed"""
        # Allow specific prefixes
        for prefix in self.allowed_prefixes:
            if key.startswith(prefix):
                return True

        # Allow common system variables
        common_vars = ['PWD', 'OLDPWD', 'CWD', 'TMPDIR', 'TEMP', 'TMP']
        if key in common_vars:
            return True

        # Allow variables that don't match sensitive patterns
        return not self._is_sensitive(key)

    def _is_path_allowed(self, filepath: str) -> bool:
        """Check if a file path is allowed to be accessed"""
        abs_path = Path(filepath).resolve()

        # Check restricted paths
        for restricted in self.restricted_paths:
            if str(abs_path).startswith(restricted):
                return False

        # Only allow .env files in project directory
        if not filepath.endswith('.env'):
            return False

        # Check if path is within project directory (basic check)
        project_root = Path(__file__).parent.parent.parent.parent
        try:
            abs_path.relative_to(project_root)
            return True
        except ValueError:
            return False

    def get_environment_variable(self, key: str) -> Dict[str, Any]:
        """Get a specific environment variable value (filtered for security)"""
        try:
            if not self._is_allowed_env_var(key):
                return {
                    'success': False,
                    'error': f'Access denied: {key} is restricted or sensitive',
                    'key': key
                }

            value = os.environ.get(key)
            if value is None:
                return {
                    'success': False,
                    'error': f'Environment variable {key} not found',
                    'key': key
                }

            return {
                'success': True,
                'key': key,
                'value': value,
                'length': len(value),
                'is_sensitive': self._is_sensitive(key, value)
            }

        except Exception as e:
            return {
                'success': False,
                'key': key,
                'error': str(e)
            }

    def list_environment_variables(self, filter_pattern: str = "") -> Dict[str, Any]:
        """List available environment variables (filtered for security)"""
        try:
            allowed_vars = {}

            for key, value in os.environ.items():
                if self._is_allowed_env_var(key):
                    if not filter_pattern or filter_pattern.lower() in key.lower():
                        allowed_vars[key] = {
                            'length': len(value),
                            'is_sensitive': self._is_sensitive(key, value)
                        }

            return {
                'success': True,
                'total_variables': len(allowed_vars),
                'variables': allowed_vars,
                'filter_applied': bool(filter_pattern)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def check_env_var_exists(self, key: str) -> Dict[str, Any]:
        """Check if an environment variable exists (without revealing value)"""
        try:
            exists = key in os.environ
            is_allowed = self._is_allowed_env_var(key)

            return {
                'success': True,
                'key': key,
                'exists': exists,
                'accessible': exists and is_allowed,
                'is_sensitive': self._is_sensitive(key) if exists else False
            }

        except Exception as e:
            return {
                'success': False,
                'key': key,
                'error': str(e)
            }

    def read_env_file(self, filepath: str) -> Dict[str, Any]:
        """Read a .env file with security filtering"""
        try:
            if not self._is_path_allowed(filepath):
                return {
                    'success': False,
                    'filepath': filepath,
                    'error': 'Access denied: file path not allowed'
                }

            if not os.path.exists(filepath):
                return {
                    'success': False,
                    'filepath': filepath,
                    'error': 'File not found'
                }

            env_vars = {}
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()

                            if self._is_allowed_env_var(key):
                                env_vars[key] = {
                                    'value': value,
                                    'line': line_num,
                                    'length': len(value),
                                    'is_sensitive': self._is_sensitive(key, value)
                                }

            return {
                'success': True,
                'filepath': filepath,
                'total_variables': len(env_vars),
                'variables': env_vars
            }

        except Exception as e:
            return {
                'success': False,
                'filepath': filepath,
                'error': str(e)
            }

    def get_project_env_info(self) -> Dict[str, Any]:
        """Get information about environment setup for the project"""
        try:
            project_root = Path(__file__).parent.parent.parent.parent

            # Look for common .env files
            env_files = []
            for env_file in ['.env', '.env.local', '.env.production', '.env.development']:
                env_path = project_root / env_file
                if env_path.exists():
                    env_files.append({
                        'name': env_file,
                        'path': str(env_path),
                        'size': env_path.stat().st_size
                    })

            # Get basic environment info
            env_info = {
                'python_version': sys.version.split()[0],
                'platform': sys.platform,
                'working_directory': str(project_root),
                'env_files_found': env_files,
                'total_env_vars': len(os.environ),
                'allowed_env_vars': sum(1 for k in os.environ.keys() if self._is_allowed_env_var(k))
            }

            return {
                'success': True,
                'project_info': env_info
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
