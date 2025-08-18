"""
I/O API
- Promotion helpers from State 2 paths to State 0 directory.
"""
from typing import List
import os
import shutil


def promote(paths: List[str], dst_dir: str) -> None:
	"""
	Promote given files to the destination directory (curated evidence).
	Creates the destination directory if it does not exist.
	Silently skips missing sources.
	"""
	if not dst_dir:
		raise ValueError("dst_dir must be provided")
	os.makedirs(dst_dir, exist_ok=True)
	for p in paths or []:
		if not p:
			continue
		if os.path.exists(p) and os.path.isfile(p):
			shutil.copy2(p, os.path.join(dst_dir, os.path.basename(p)))
