
#!/usr/bin/env python3
"""
HoloIndex CLI Entry Point
Maintains backward compatibility while using the new module structure.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===

if __name__ == "__main__":
    from holo_index.cli import main
    main()