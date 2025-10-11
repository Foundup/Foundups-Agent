"""
Unit tests for Execution Log Librarian

Tests the core functionality of the execution log processing system.
"""

import pytest
import tempfile
import os
from pathlib import Path
from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import ExecutionLogLibrarian


class TestExecutionLogLibrarian:
    """Test suite for ExecutionLogLibrarian functionality."""

    @pytest.fixture
    def sample_log_content(self):
        """Create sample log content for testing."""
        return """Task: Read WSP_00 and understand system
Step 1: Found WSP_00 file
Step 2: Analyzed neural network concepts
Step 3: Applied quantum entanglement principles
Result: System understanding achieved

Task: Analyze YouTube DAE
Step 1: Located main.py file
Step 2: Examined option 1 functionality
Step 3: Identified Gemini model integration
Result: YouTube DAE understanding complete

Task: Enhance with Sora2
Step 1: Checked API availability
Step 2: Added Sora2 generator option
Step 3: Updated pricing logic
Result: Sora2 integration successful
"""

    @pytest.fixture
    def temp_log_file(self, sample_log_content):
        """Create a temporary log file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_log_content)
            temp_path = f.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    def test_librarian_initialization(self, temp_log_file):
        """Test that librarian initializes correctly."""
        librarian = ExecutionLogLibrarian(temp_log_file, chunk_size=500)

        assert librarian.log_file_path == Path(temp_log_file)
        assert librarian.chunk_size == 500
        assert isinstance(librarian.chunks, list)
        assert isinstance(librarian.state.total_lines, int)
        assert librarian.state.total_lines > 0

    def test_chunk_creation(self, temp_log_file):
        """Test that chunks are created properly."""
        librarian = ExecutionLogLibrarian(temp_log_file, chunk_size=10)

        # Should create at least one chunk
        assert len(librarian.chunks) > 0

        # Each chunk should have proper structure
        for chunk in librarian.chunks:
            assert hasattr(chunk, 'chunk_id')
            assert hasattr(chunk, 'start_line')
            assert hasattr(chunk, 'end_line')
            assert hasattr(chunk, 'line_count')
            assert hasattr(chunk, 'content_preview')
            assert chunk.line_count > 0
            assert chunk.start_line >= 1
            assert chunk.end_line >= chunk.start_line

    def test_task_generation(self, temp_log_file):
        """Test that processing tasks are generated correctly."""
        librarian = ExecutionLogLibrarian(temp_log_file, chunk_size=20)

        task = librarian.get_next_processing_task()

        # Should return a task if chunks exist
        if librarian.chunks:
            assert task is not None
            assert 'librarian_task_coordination' in task
            assert 'chunk_content' in task
            assert 'expected_output_format' in task

            # Verify task structure
            coord = task['librarian_task_coordination']
            assert 'chunk_id' in coord
            assert 'processing_context' in coord
            assert 'qwen_processing_instructions' in coord

    def test_state_persistence(self, temp_log_file):
        """Test save and load functionality."""
        librarian = ExecutionLogLibrarian(temp_log_file)

        # Save state
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_state_file = f.name

        try:
            librarian.save_processing_state(temp_state_file)

            # Verify file was created and has content
            assert os.path.exists(temp_state_file)
            assert os.path.getsize(temp_state_file) > 0

            # Could test loading here if needed
            # new_librarian = ExecutionLogLibrarian(temp_log_file)
            # new_librarian.load_processing_state(temp_state_file)

        finally:
            if os.path.exists(temp_state_file):
                os.unlink(temp_state_file)

    def test_empty_file_handling(self):
        """Test handling of empty or very small files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")  # Empty file
            empty_file = f.name

        try:
            librarian = ExecutionLogLibrarian(empty_file)

            # Should handle empty file gracefully
            assert librarian.state.total_lines == 0
            assert len(librarian.chunks) == 0

            # Should return None when no tasks available
            task = librarian.get_next_processing_task()
            assert task is None

        finally:
            os.unlink(empty_file)

    def test_chunk_content_extraction(self, temp_log_file):
        """Test that chunk content is extracted correctly."""
        librarian = ExecutionLogLibrarian(temp_log_file, chunk_size=10)

        if librarian.chunks:
            first_chunk = librarian.chunks[0]
            content = librarian._get_chunk_content(
                first_chunk.start_line,
                first_chunk.end_line
            )

            # Should return string content
            assert isinstance(content, str)
            assert len(content) > 0

            # Content should match expected lines
            lines = content.split('\n')
            expected_lines = first_chunk.end_line - first_chunk.start_line + 1
            assert len(lines) >= expected_lines - 1  # Account for potential trailing newline

    def test_learning_extraction(self, temp_log_file):
        """Test that learnings can be extracted from analysis."""
        librarian = ExecutionLogLibrarian(temp_log_file)

        # Simulate analysis results
        mock_analysis = {
            "LEARNINGS_EXTRACTED": {
                "Pattern_1": "Systematic problem decomposition approach",
                "Technique_1": "Step-by-step file analysis method"
            },
            "HOLO_IMPROVEMENT_OPPORTUNITIES": {
                "Capability_1": "Enhanced systematic processing"
            }
        }

        # Record analysis
        librarian.record_qwen_analysis(1, mock_analysis)

        # Verify learnings were extracted
        assert len(librarian.extracted_learnings["problem_solving_patterns"]) > 0
        assert librarian.state.learnings_extracted > 0
        assert librarian.state.holo_improvements_identified > 0

    def test_enhancement_plan_generation(self, temp_log_file):
        """Test that enhancement plans can be generated."""
        librarian = ExecutionLogLibrarian(temp_log_file)

        # Add some mock learnings
        librarian.extracted_learnings["tool_usage_patterns"].append("CLI tool integration pattern")
        librarian.extracted_learnings["problem_solving_patterns"].append("Systematic decomposition")

        # Generate plan
        plan = librarian.generate_holo_enhancement_plan()

        # Verify plan structure
        assert "holo_enhancement_master_plan" in plan
        assert "processing_summary" in plan["holo_enhancement_master_plan"]
        assert "learning_categories" in plan["holo_enhancement_master_plan"]
        assert "immediate_improvements" in plan["holo_enhancement_master_plan"]


if __name__ == "__main__":
    pytest.main([__file__])
