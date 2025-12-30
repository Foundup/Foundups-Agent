import os


from modules.infrastructure.instance_lock.src.instance_manager import InstanceLock


class _FakeProc:
    def __init__(self, info: dict):
        self.info = info


def test_check_duplicates_ignores_parent_shell_processes(monkeypatch):
    """
    Windows commonly shows parent shells (e.g. bash.exe) whose cmdline contains
    "python main.py --youtube". Those shells must NOT be counted as duplicates.
    """
    lock = InstanceLock("youtube_monitor")

    fake_current_pid = 9999
    monkeypatch.setattr(os, "getpid", lambda: fake_current_pid)

    procs = [
        _FakeProc(
            {
                "pid": 100,
                "name": "bash.exe",
                "exe": r"C:\Program Files\Git\bin\bash.exe",
                "cmdline": ["bash.exe", "-lc", "python main.py --youtube"],
                "create_time": 0,
            }
        ),
        _FakeProc(
            {
                "pid": 101,
                "name": "python.exe",
                "exe": r"C:\Python312\python.exe",
                "cmdline": [r"C:\Python312\python.exe", "main.py", "--youtube"],
                "create_time": 0,
            }
        ),
    ]

    import psutil

    monkeypatch.setattr(psutil, "process_iter", lambda *_args, **_kwargs: iter(procs))

    assert lock.check_duplicates(quiet=True) == [101]


def test_check_duplicates_requires_youtube_flag_or_auto_moderator(monkeypatch):
    lock = InstanceLock("youtube_monitor")

    fake_current_pid = 9999
    monkeypatch.setattr(os, "getpid", lambda: fake_current_pid)

    procs = [
        _FakeProc(
            {
                "pid": 201,
                "name": "python.exe",
                "exe": r"C:\Python312\python.exe",
                "cmdline": [r"C:\Python312\python.exe", "main.py"],
                "create_time": 0,
            }
        ),
        _FakeProc(
            {
                "pid": 202,
                "name": "python.exe",
                "exe": r"C:\Python312\python.exe",
                "cmdline": [r"C:\Python312\python.exe", "-m", "modules.communication.livechat.src.auto_moderator_dae"],
                "create_time": 0,
            }
        ),
    ]

    import psutil

    monkeypatch.setattr(psutil, "process_iter", lambda *_args, **_kwargs: iter(procs))

    assert lock.check_duplicates(quiet=True) == [202]


def test_kill_pids_reports_results(monkeypatch):
    lock = InstanceLock("youtube_monitor")

    killed: list[int] = []

    monkeypatch.setattr(lock, "_kill_process", lambda pid: killed.append(pid))
    monkeypatch.setattr(lock, "_is_process_running", lambda pid: False)

    result = lock.kill_pids([123, 456], wait_seconds=0)
    assert result["requested"] == [123, 456]
    assert killed == [123, 456]
    assert result["killed"] == [123, 456]
    assert result["still_running"] == []










