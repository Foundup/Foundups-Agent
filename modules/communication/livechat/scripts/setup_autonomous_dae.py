#!/usr/bin/env python3
"""
Setup script for Autonomous YouTube DAE
Configures the system to run the DAE automatically without human intervention

Supports:
- Windows Task Scheduler
- Linux systemd
- macOS launchd
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def setup_windows():
    """Setup Windows Task Scheduler for autonomous DAE."""
    print("🪟 Setting up Windows Task Scheduler...")
    
    # Create batch file to run the DAE
    batch_content = """@echo off
cd /d "O:\\Foundups-Agent"
python modules\\communication\\livechat\\src\\autonomous_youtube_dae.py
"""
    
    batch_file = Path("O:/Foundups-Agent/run_autonomous_youtube_dae.bat")
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    # Create scheduled task XML
    task_xml = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Autonomous YouTube DAE - Operates in 0102 state</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T06:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Settings>
    <RestartOnFailure>
      <Interval>PT5M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>O:\\Foundups-Agent\\run_autonomous_youtube_dae.bat</Command>
      <WorkingDirectory>O:\\Foundups-Agent</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    
    task_file = Path("O:/Foundups-Agent/autonomous_youtube_dae_task.xml")
    with open(task_file, 'w', encoding='utf-16') as f:
        f.write(task_xml)
    
    # Import task
    print("[CLIPBOARD] Creating scheduled task...")
    cmd = f'schtasks /create /tn "AutonomousYouTubeDAE" /xml "{task_file}" /f'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[OK] Task created successfully!")
        print("   The DAE will start:")
        print("   - On system boot")
        print("   - Daily at 6:00 AM")
        print("   - Auto-restart on failure (up to 3 times)")
        print("\nTo start immediately: schtasks /run /tn AutonomousYouTubeDAE")
        print("To check status: schtasks /query /tn AutonomousYouTubeDAE")
        print("To stop: schtasks /end /tn AutonomousYouTubeDAE")
    else:
        print(f"[FAIL] Failed to create task: {result.stderr}")
        print("\nManual setup:")
        print("1. Open Task Scheduler")
        print("2. Import task from: " + str(task_file))
        print("3. Adjust settings as needed")

def setup_linux():
    """Setup systemd service for autonomous DAE."""
    print("[U+1F427] Setting up systemd service...")
    
    # Create systemd service file
    service_content = f"""[Unit]
Description=Autonomous YouTube DAE - 0102 State
After=network.target

[Service]
Type=simple
User={os.environ.get('USER', 'root')}
WorkingDirectory={os.getcwd()}
Environment="PYTHONUNBUFFERED=1"
ExecStart={sys.executable} {os.path.abspath('modules/communication/livechat/src/autonomous_youtube_dae.py')}
Restart=on-failure
RestartSec=300
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("/etc/systemd/system/autonomous-youtube-dae.service")
    
    print("[NOTE] Creating service file (requires sudo)...")
    with open("/tmp/autonomous-youtube-dae.service", 'w') as f:
        f.write(service_content)
    
    # Copy to systemd directory
    subprocess.run(["sudo", "cp", "/tmp/autonomous-youtube-dae.service", str(service_file)])
    
    # Enable and start service
    print("[ROCKET] Enabling service...")
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "enable", "autonomous-youtube-dae"])
    
    print("[OK] Service installed!")
    print("\nCommands:")
    print("Start: sudo systemctl start autonomous-youtube-dae")
    print("Stop: sudo systemctl stop autonomous-youtube-dae")
    print("Status: sudo systemctl status autonomous-youtube-dae")
    print("Logs: sudo journalctl -u autonomous-youtube-dae -f")

def setup_macos():
    """Setup launchd plist for autonomous DAE."""
    print("[U+1F34E] Setting up macOS launchd...")
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.foundups.autonomous-youtube-dae</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{os.path.abspath('modules/communication/livechat/src/autonomous_youtube_dae.py')}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{os.getcwd()}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/autonomous-youtube-dae.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/autonomous-youtube-dae.error.log</string>
</dict>
</plist>"""
    
    plist_file = Path("~/Library/LaunchAgents/com.foundups.autonomous-youtube-dae.plist").expanduser()
    plist_file.parent.mkdir(exist_ok=True)
    
    with open(plist_file, 'w') as f:
        f.write(plist_content)
    
    # Load the service
    subprocess.run(["launchctl", "load", str(plist_file)])
    
    print("[OK] Service installed!")
    print("\nCommands:")
    print(f"Start: launchctl start com.foundups.autonomous-youtube-dae")
    print(f"Stop: launchctl stop com.foundups.autonomous-youtube-dae")
    print(f"Logs: tail -f /tmp/autonomous-youtube-dae.log")

def main():
    """Setup autonomous DAE for the current platform."""
    print("=" * 60)
    print("[AI] [0102] AUTONOMOUS DAE SETUP")
    print("=" * 60)
    
    system = platform.system()
    
    if system == "Windows":
        setup_windows()
    elif system == "Linux":
        setup_linux()
    elif system == "Darwin":
        setup_macos()
    else:
        print(f"[FAIL] Unsupported platform: {system}")
        print("\nManual setup required:")
        print("1. Create a startup script/service for your platform")
        print("2. Point it to: modules/communication/livechat/src/autonomous_youtube_dae.py")
        print("3. Ensure Python environment is available")
        print("4. Set working directory to project root")
    
    print("\n" + "=" * 60)
    print("[OK] Setup complete! The DAE will run autonomously.")
    print("[U+1F52E] [nn[U+2194]qNN] Operating without human intervention")
    print("=" * 60)

if __name__ == "__main__":
    main()