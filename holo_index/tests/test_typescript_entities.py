#!/usr/bin/env python3
"""Regression tests for TypeScript entity extraction (WSP 87 compliance)."""

import os
import textwrap
import tempfile
import unittest
from pathlib import Path

from holo_index.core.holo_index import HoloIndex, parse_typescript_entities


SAMPLE_TS = textwrap.dedent(
    """
    import React from 'react';

    export function HandlePressStart() {
      return null;
    }

    const HandleClassify = async () => {
      return true;
    };

    const useCaptureItem = () => ({});

    export interface ClassificationItem {
      id: string;
    }

    const [pendingClassificationItem, setPendingClassificationItem] = useState(null);
    """
).strip("\n")


class TestTypeScriptEntities(unittest.TestCase):
    """Validate TypeScript entity parsing heuristics."""

    def test_parse_typescript_entities_captures_components_hooks_and_interfaces(self):
        lines = SAMPLE_TS.splitlines()
        entities = parse_typescript_entities(lines, context=2)

        self.assertIn("handlepressstart", entities)
        self.assertIn("handleclassify", entities)
        self.assertIn("usecaptureitem", entities)
        self.assertIn("classificationitem", entities)
        self.assertIn("pendingclassificationitem", entities)
        self.assertIn("setpendingclassificationitem", entities)

        preview = entities["handlepressstart"]["preview"]
        self.assertIn("HandlePressStart", preview)
        self.assertGreater(entities["handlepressstart"]["line"], 0)

    def test_extract_typescript_entities_reads_and_caches_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "App.tsx"
            file_path.write_text(SAMPLE_TS, encoding="utf-8")

            holo = HoloIndex.__new__(HoloIndex)
            holo._ts_entity_cache = {}

            first = HoloIndex._extract_typescript_entities(holo, file_path)
            self.assertIn("handlepressstart", first)
            self.assertNotIn("extrathing", first)

            # Update file to ensure cache invalidation picks up new entities
            updated = SAMPLE_TS + "\nconst ExtraThing = () => null;"
            file_path.write_text(updated, encoding="utf-8")
            os.utime(file_path, None)

            second = HoloIndex._extract_typescript_entities(holo, file_path)
            self.assertIn("extrathing", second)


if __name__ == "__main__":
    unittest.main()
