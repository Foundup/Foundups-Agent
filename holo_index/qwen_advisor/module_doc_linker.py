# -*- coding: utf-8 -*-
"""
Qwen Module Documentation Linker - Autonomous Intelligent Document Binding
===========================================================================

WSP References: WSP 87 (HoloIndex), WSP 22 (ModLog), WSP 3 (Module Organization)

Purpose:
    Autonomous intelligent agent that discovers, analyzes, and links module
    documentation using Qwen advisor. Runs automatically on index refresh or
    on-demand for specific modules.

Architecture:
    - Separation of Concerns: HoloIndex stores, Qwen analyzes
    - Autonomous Operation: Runs automatically without human intervention
    - Idempotent: Safe to run multiple times
    - Intelligent: Uses Qwen LLM for understanding document relationships

Operation Levels:
    Level 0: Fully Automatic (runs on --index-all)
    Level 1: On-Demand (python holo_index.py link-modules --module [name])
    Level 2: Interactive (--interactive flag for verification)
    Level 3: Manual Override (edit registry JSON, Qwen validates)

Output:
    - Enhanced ChromaDB metadata with module ownership
    - MODULE_DOC_REGISTRY.json per module
    - Bidirectional document relationship graph

Author: 0102 DAE (Infrastructure Orchestration)
Created: 2025-10-11
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import re
from datetime import datetime

# HoloIndex imports
from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator


@dataclass
class DocumentMetadata:
    """Metadata for a single document within a module."""
    doc_type: str  # modlog, readme, roadmap, interface, wsp_protocol, documentation, test_documentation, other
    file_path: str
    title: str
    purpose: str
    related_docs: List[str]  # File paths of related documents
    cross_references: List[str]  # WSP numbers, module names referenced
    last_updated: str


@dataclass
class ModuleDocumentRegistry:
    """Complete documentation registry for a single module."""
    module_name: str
    module_path: str
    module_domain: str
    documents: List[DocumentMetadata]
    relationships: Dict[str, List[str]]  # doc_path -> [related_doc_paths]
    wsp_implementations: List[str]  # WSP numbers implemented in this module
    linked_timestamp: str
    linker_version: str = "1.0.0"


class QwenModuleDocLinker:
    """
    Autonomous intelligent agent for discovering and linking module documentation.

    Uses Qwen advisor to understand document relationships and enrich HoloIndex
    metadata with module ownership and cross-references.
    """

    def __init__(self, repo_root: Path, holo_coordinator: HoloDAECoordinator, agent_db=None):
        """
        Initialize the Qwen Module Documentation Linker.

        Args:
            repo_root: Path to repository root (O:\Foundups-Agent)
            holo_coordinator: HoloDAE coordinator for Qwen LLM access
            agent_db: AgentDB instance (will create if None)
        """
        self.repo_root = Path(repo_root)
        self.modules_dir = self.repo_root / "modules"
        self.holo_coordinator = holo_coordinator
        self.linker_version = "1.0.0"

        # Initialize AgentDB
        if agent_db is None:
            from modules.infrastructure.database.src.agent_db import AgentDB
            self.db = AgentDB()
        else:
            self.db = agent_db

    def discover_all_modules(self) -> List[Path]:
        """
        Discover all WSP 49 compliant modules in modules/ directory.

        Returns:
            List of Path objects to module directories
        """
        if not self.modules_dir.exists():
            return []

        modules = []
        for domain_dir in self.modules_dir.iterdir():
            if not domain_dir.is_dir():
                continue
            if domain_dir.name.startswith('.'):
                continue

            for module_dir in domain_dir.iterdir():
                if not module_dir.is_dir():
                    continue
                if module_dir.name.startswith('.'):
                    continue

                # Check for WSP 49 compliance (README.md exists)
                if (module_dir / "README.md").exists():
                    modules.append(module_dir)

        return sorted(modules)

    def analyze_module_docs(self, module_path: Path) -> Dict:
        """
        Analyze all documentation in a module using Qwen.

        Args:
            module_path: Path to module directory

        Returns:
            Dictionary with module analysis results
        """
        module_name = module_path.name
        module_domain = module_path.parent.name

        # Find all documentation files
        doc_files = self._find_module_docs(module_path)

        print(f"[OK] Analyzing {len(doc_files)} documents in {module_domain}/{module_name}")

        documents = []
        for doc_path in doc_files:
            doc_metadata = self._qwen_extract_doc_metadata(doc_path)
            if doc_metadata:
                documents.append(doc_metadata)

        return {
            "module_name": module_name,
            "module_path": str(module_path),
            "module_domain": module_domain,
            "documents": documents
        }

    def _find_module_docs(self, module_path: Path) -> List[Path]:
        """
        Find all documentation files in a module.

        Args:
            module_path: Path to module directory

        Returns:
            List of Path objects to documentation files
        """
        doc_patterns = [
            "README.md",
            "INTERFACE.md",
            "ModLog.md",
            "ROADMAP.md",
            "docs/**/*.md",
            "tests/README.md",
            "tests/TestModLog.md"
        ]

        doc_files = []
        for pattern in doc_patterns:
            if "**" in pattern:
                # Recursive glob
                doc_files.extend(module_path.glob(pattern))
            else:
                # Direct path
                doc_file = module_path / pattern
                if doc_file.exists():
                    doc_files.append(doc_file)

        return sorted(doc_files)

    def _qwen_extract_doc_metadata(self, doc_path: Path) -> Optional[DocumentMetadata]:
        """
        Use Qwen to extract metadata from a document.

        Args:
            doc_path: Path to document

        Returns:
            DocumentMetadata object or None if extraction fails
        """
        try:
            # Read document content
            content = doc_path.read_text(encoding='utf-8')

            # Classify document type
            doc_type = self._classify_doc_type(doc_path, content)

            # Extract title (first heading)
            title = self._extract_title(content)

            # Use Qwen to understand document purpose and relationships
            qwen_analysis = self._qwen_analyze_document(doc_path, content, doc_type)

            # Build metadata
            metadata = DocumentMetadata(
                doc_type=doc_type,
                file_path=str(doc_path),
                title=title,
                purpose=qwen_analysis.get("purpose", ""),
                related_docs=qwen_analysis.get("related_docs", []),
                cross_references=qwen_analysis.get("cross_references", []),
                last_updated=datetime.now().isoformat()
            )

            return metadata

        except Exception as e:
            print(f"[WARNING] Failed to extract metadata from {doc_path}: {e}")
            return None

    def _classify_doc_type(self, doc_path: Path, content: str) -> str:
        """
        Classify document type based on filename and content.

        Args:
            doc_path: Path to document
            content: Document content

        Returns:
            Document type string (aligned with HoloIndex classification)
        """
        filename = doc_path.name.lower()

        # WSP protocol
        if "wsp_" in filename and filename.endswith(".md"):
            return "wsp_protocol"

        # Module documentation
        if filename == "readme.md":
            return "module_readme"
        if filename == "interface.md":
            return "interface"
        if filename == "modlog.md":
            return "modlog"
        if filename == "roadmap.md":
            return "roadmap"

        # Test documentation
        if "test" in str(doc_path).lower():
            return "test_documentation"

        # General documentation
        if "docs" in str(doc_path).lower():
            return "documentation"

        return "other"

    def _extract_title(self, content: str) -> str:
        """
        Extract title from document (first # heading).

        Args:
            content: Document content

        Returns:
            Title string
        """
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()

        return "Untitled"

    def _qwen_analyze_document(self, doc_path: Path, content: str, doc_type: str) -> Dict:
        """
        Use Qwen LLM to analyze document and extract relationships.

        Args:
            doc_path: Path to document
            content: Document content
            doc_type: Document type classification

        Returns:
            Dictionary with analysis results (purpose, related_docs, cross_references)
        """
        # Build Qwen prompt
        prompt = f"""Analyze this {doc_type} document and extract:

1. PURPOSE: One-sentence summary of what this document does
2. RELATED_DOCS: Other documentation files referenced (README.md, INTERFACE.md, etc.)
3. CROSS_REFERENCES: WSP protocol numbers (WSP XX), module names, or other system references

Document path: {doc_path}
Document type: {doc_type}

Content (first 1000 chars):
{content[:1000]}

Respond in JSON format:
{{
    "purpose": "One sentence summary",
    "related_docs": ["README.md", "INTERFACE.md"],
    "cross_references": ["WSP 22", "WSP 49", "holo_index"]
}}
"""

        try:
            # Use HoloDAE coordinator to query Qwen
            response = self.holo_coordinator.query_qwen(prompt)

            # Parse JSON response
            analysis = json.loads(response)

            return analysis

        except Exception as e:
            print(f"[WARNING] Qwen analysis failed for {doc_path}: {e}")

            # Fallback: Simple regex-based extraction
            return self._fallback_analyze_document(content)

    def _fallback_analyze_document(self, content: str) -> Dict:
        r"""
        Fallback document analysis using regex patterns.

        Args:
            content: Document content

        Returns:
            Dictionary with analysis results
        """
        # Extract WSP references
        wsp_pattern = r'WSP[- ]?\d+'
        wsp_refs = list(set(re.findall(wsp_pattern, content, re.IGNORECASE)))

        # Extract common doc references
        doc_pattern = r'(README\.md|INTERFACE\.md|ModLog\.md|ROADMAP\.md)'
        doc_refs = list(set(re.findall(doc_pattern, content, re.IGNORECASE)))

        # Extract purpose from first paragraph
        lines = content.split('\n')
        purpose = ""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                purpose = line[:200]  # First 200 chars
                break

        return {
            "purpose": purpose or "No description available",
            "related_docs": doc_refs,
            "cross_references": wsp_refs
        }

    def build_relationship_graph(self, module_analysis: Dict) -> Dict[str, List[str]]:
        """
        Build bidirectional relationship graph between documents.

        Args:
            module_analysis: Module analysis dictionary from analyze_module_docs()

        Returns:
            Dictionary mapping doc_path -> [related_doc_paths]
        """
        relationships = {}
        documents = module_analysis["documents"]
        module_path = Path(module_analysis["module_path"])

        for doc in documents:
            doc_path = doc.file_path
            related_paths = []

            # Resolve related doc references to full paths
            for related_doc in doc.related_docs:
                # Try to find the document in the module
                potential_paths = [
                    module_path / related_doc,
                    module_path / "docs" / related_doc,
                    module_path / "tests" / related_doc
                ]

                for potential_path in potential_paths:
                    if potential_path.exists():
                        related_paths.append(str(potential_path))
                        break

            relationships[doc_path] = related_paths

        return relationships

    def enrich_holo_metadata(self, module_analysis: Dict, relationships: Dict):
        """
        Enrich HoloIndex ChromaDB metadata with module ownership and relationships.

        This method would update the ChromaDB collection with enhanced metadata.
        For now, it's a placeholder showing what data would be added.

        Args:
            module_analysis: Module analysis dictionary
            relationships: Relationship graph
        """
        print(f"[INFO] ChromaDB enrichment placeholder - would add:")
        print(f"  - module_path: {module_analysis['module_path']}")
        print(f"  - module_name: {module_analysis['module_name']}")
        print(f"  - module_domain: {module_analysis['module_domain']}")
        print(f"  - related_docs: {len(relationships)} relationship entries")

        # TODO: Integrate with actual ChromaDB update
        # This would require accessing the HoloIndex ChromaDB collection
        # and updating metadata for each document

    def generate_module_registry(self, module_analysis: Dict, relationships: Dict) -> ModuleDocumentRegistry:
        """
        Generate MODULE_DOC_REGISTRY.json for a module.

        Args:
            module_analysis: Module analysis dictionary
            relationships: Relationship graph

        Returns:
            ModuleDocumentRegistry object
        """
        # Extract WSP implementations from all documents
        wsp_implementations = set()
        for doc in module_analysis["documents"]:
            for cross_ref in doc.cross_references:
                if cross_ref.upper().startswith("WSP"):
                    wsp_implementations.add(cross_ref)

        # Build registry
        registry = ModuleDocumentRegistry(
            module_name=module_analysis["module_name"],
            module_path=module_analysis["module_path"],
            module_domain=module_analysis["module_domain"],
            documents=module_analysis["documents"],
            relationships=relationships,
            wsp_implementations=sorted(list(wsp_implementations)),
            linked_timestamp=datetime.now().isoformat(),
            linker_version=self.linker_version
        )

        return registry

    def save_module_registry(self, registry: ModuleDocumentRegistry):
        """
        Save module documentation registry to AgentDB.

        Args:
            registry: ModuleDocumentRegistry object to save
        """
        # Register module in database
        module_id = self.db.register_module(
            module_name=registry.module_name,
            module_path=registry.module_path,
            module_domain=registry.module_domain,
            linker_version=registry.linker_version
        )

        # Register all documents
        doc_id_map = {}  # file_path -> doc_id
        for doc in registry.documents:
            doc_id = self.db.register_document(
                module_id=module_id,
                doc_type=doc.doc_type,
                file_path=doc.file_path,
                title=doc.title,
                purpose=doc.purpose
            )
            doc_id_map[doc.file_path] = doc_id

            # Add cross-references
            for cross_ref in doc.cross_references:
                # Determine reference type
                if cross_ref.upper().startswith("WSP"):
                    ref_type = "wsp"
                elif any(domain in cross_ref.lower() for domain in ["communication", "infrastructure", "ai_intelligence", "platform_integration"]):
                    ref_type = "module"
                else:
                    ref_type = "other"

                self.db.add_cross_reference(doc_id, ref_type, cross_ref)

        # Add document relationships
        for from_path, to_paths in registry.relationships.items():
            if from_path in doc_id_map:
                from_doc_id = doc_id_map[from_path]
                for to_path in to_paths:
                    if to_path in doc_id_map:
                        to_doc_id = doc_id_map[to_path]
                        self.db.add_document_relationship(from_doc_id, to_doc_id)

        # Add WSP implementations
        for wsp_number in registry.wsp_implementations:
            self.db.add_wsp_implementation(module_id, wsp_number)

        print(f"[OK] Registry saved to database: module_id={module_id}")

    def link_single_module(self, module_name: str, interactive: bool = False, force: bool = False) -> bool:
        """
        Link documentation for a single module.

        Args:
            module_name: Name of module to link (or path like "communication/liberty_alert")
            interactive: Interactive verification mode
            force: Force relink even if already linked

        Returns:
            True if linking successful, False otherwise
        """
        # Find module path
        if '/' in module_name:
            # Full path provided
            module_path = self.modules_dir / module_name
        else:
            # Search for module by name
            modules = self.discover_all_modules()
            matching_modules = [m for m in modules if m.name == module_name]

            if not matching_modules:
                print(f"[FAIL] Module not found: {module_name}")
                return False

            if len(matching_modules) > 1:
                print(f"[WARNING] Multiple modules found with name '{module_name}':")
                for m in matching_modules:
                    print(f"  - {m.parent.name}/{m.name}")
                print("[FAIL] Please specify full path: domain/module")
                return False

            module_path = matching_modules[0]

        if not module_path.exists():
            print(f"[FAIL] Module path does not exist: {module_path}")
            return False

        # Check if already linked in database
        existing_module = self.db.get_module(module_path=str(module_path))
        if existing_module and not force:
            print(f"[INFO] Module already linked: {module_path.name}")
            print(f"[INFO] Use --force to relink")
            return True

        print(f"\n[OK] Linking module: {module_path.parent.name}/{module_path.name}")

        # Phase 1: Analyze module documentation
        module_analysis = self.analyze_module_docs(module_path)

        if interactive:
            print(f"\n[INFO] Found {len(module_analysis['documents'])} documents:")
            for doc in module_analysis['documents']:
                print(f"  - {doc.doc_type}: {doc.title}")

            response = input("\n[?] Continue with linking? (y/n): ")
            if response.lower() != 'y':
                print("[INFO] Linking cancelled by user")
                return False

        # Phase 2: Build relationship graph
        relationships = self.build_relationship_graph(module_analysis)

        # Phase 3: Enrich HoloIndex metadata (placeholder)
        self.enrich_holo_metadata(module_analysis, relationships)

        # Phase 4: Generate and save registry
        registry = self.generate_module_registry(module_analysis, relationships)
        self.save_module_registry(registry)

        print(f"[OK] Module linked successfully: {module_path.name}")
        print(f"[OK] Documents: {len(registry.documents)}")
        print(f"[OK] WSP implementations: {len(registry.wsp_implementations)}")

        return True

    def link_all_modules(self, interactive: bool = False, force: bool = False) -> Dict[str, bool]:
        """
        Link documentation for all modules in repository.

        Args:
            interactive: Interactive verification mode
            force: Force relink even if already linked

        Returns:
            Dictionary mapping module_name -> success status
        """
        modules = self.discover_all_modules()

        print(f"\n[OK] Discovered {len(modules)} modules")

        if interactive:
            print("\n[INFO] Modules to link:")
            for module in modules:
                print(f"  - {module.parent.name}/{module.name}")

            response = input("\n[?] Continue with linking all modules? (y/n): ")
            if response.lower() != 'y':
                print("[INFO] Linking cancelled by user")
                return {}

        results = {}
        for module in modules:
            module_key = f"{module.parent.name}/{module.name}"
            success = self.link_single_module(module_key, interactive=False, force=force)
            results[module_key] = success

        # Summary
        success_count = sum(1 for v in results.values() if v)
        print(f"\n[OK] Linking complete: {success_count}/{len(modules)} modules linked")

        return results


# CLI integration would be added to holo_index/cli.py
def main():
    """Test harness for development."""
    from pathlib import Path

    # Mock HoloDAE coordinator for testing
    class MockHoloDAE:
        def query_qwen(self, prompt: str) -> str:
            return json.dumps({
                "purpose": "Test document for development",
                "related_docs": ["README.md"],
                "cross_references": ["WSP 22", "WSP 49"]
            })

    repo_root = Path("O:/Foundups-Agent")
    coordinator = MockHoloDAE()

    linker = QwenModuleDocLinker(repo_root, coordinator)

    # Test on Liberty Alert module
    linker.link_single_module("communication/liberty_alert", interactive=False, force=True)


if __name__ == "__main__":
    main()
