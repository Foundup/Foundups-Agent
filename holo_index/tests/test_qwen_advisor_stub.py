import os
from pathlib import Path

import pytest

from holo_index.qwen_advisor import HoloDAECoordinator
from holo_index.qwen_advisor.models.monitoring_types import MonitoringResult


@pytest.fixture()
def coordinator():
    coord = HoloDAECoordinator()
    return coord


def test_handle_request_updates_work_context(coordinator):
    search_results = {
        'code': [
            {'location': 'modules/demo/sample_module/main.py'},
            {'location': 'holo_index/qwen_advisor/services/context_analyzer.py'},
        ]
    }

    report = coordinator.handle_holoindex_request('audit sample module', search_results)

    assert '[WORK-CONTEXT]' in report
    summary = coordinator.current_work_context.get_summary()
    assert 'modules/demo/sample_module' in summary
    assert coordinator.mps_arbitrator.decision_history, 'Expected arbitration decisions to be recorded'


def test_run_monitoring_cycle_records_changes(tmp_path, coordinator):
    watched_dir = tmp_path / 'watched'
    watched_dir.mkdir()
    tracked_file = watched_dir / 'example.py'
    tracked_file.write_text('print("hello world")\n', encoding='utf-8')

    coordinator.file_watcher.watch_paths = [str(watched_dir)]

    result = coordinator.run_monitoring_cycle()

    assert isinstance(result, MonitoringResult)
    assert coordinator.last_monitoring_result is result
    recorded_paths = {change.file_path for change in result.changes_detected}
    assert str(tracked_file) in recorded_paths
    assert coordinator.current_work_context.active_files, 'Monitoring cycle should update work context'
