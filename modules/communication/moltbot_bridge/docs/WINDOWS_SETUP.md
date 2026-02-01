# Moltbot Windows (WSL2) Installation Guide

> [!IMPORTANT]
> Moltbot runs on Windows via **WSL2** (Windows Subsystem for Linux).
> The Gateway runs inside WSL, accessible from Windows.

## Quick Install

### Step 1: Install WSL2 + Ubuntu

Open PowerShell as Administrator:
```powershell
wsl --install -d Ubuntu-24.04
```

Restart your computer if prompted.

### Step 2: Enable systemd (Required for Gateway)

Inside WSL (Ubuntu terminal):
```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Then in PowerShell:
```powershell
wsl --shutdown
```

Restart WSL to apply.

### Step 3: Install Node.js in WSL

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install -g pnpm
```

### Step 4: Install Moltbot

```bash
git clone https://github.com/moltbot/moltbot.git
cd moltbot
pnpm install
pnpm ui:build
pnpm build
moltbot onboard
```

### Step 5: Install Gateway Service

```bash
moltbot onboard --install-daemon
```

Verify:
```bash
moltbot gateway status
```

---

## Accessing Moltbot from Windows

The Gateway runs on `ws://127.0.0.1:18789` inside WSL.
WSL2 shares `localhost` with Windows, so you can access it directly.

## Configuration Location

```bash
# Inside WSL
~/.clawdbot/moltbot.json

# From Windows (if needed)
\\wsl$\Ubuntu-24.04\home\<username>\.clawdbot\moltbot.json
```

## What is WHATSAPP_ALLOWED_NUMBER?

WhatsApp uses an **allowlist** for security. Only phone numbers in `allowFrom` can message 012.

```json
{
  "channels": {
    "whatsapp": {
      "dmPolicy": "allowlist",
      "allowFrom": ["+81XXXXXXXXXX", "+1234567890"]
    }
  }
}
```

- `+81XXXXXXXXXX` - 012's personal WhatsApp number
- Add multiple numbers to allow family, team, etc.
- Use international format with `+` prefix

---

## WSL Tips

```powershell
# Enter WSL
wsl

# Check Moltbot status
wsl -e moltbot gateway status

# Shutdown WSL
wsl --shutdown
```
