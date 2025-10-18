# WRE Claude Code Integration - Installation Guide

Complete setup guide for running WRE as a "skin" for Claude Code with "Run WRE" functionality.

## Quick Install

### 1. **Install Extension**
```bash
# Navigate to extension directory
cd O:\Foundups-Agent\extensions\claude_wre

# Install dependencies  
npm install

# Compile TypeScript
npm run compile
```

### 2. **Install in VS Code**
```bash
# Option A: Development mode (for testing)
# Open extensions/claude_wre in VS Code and press F5

# Option B: Package and install
vsce package
code --install-extension claude-wre-integration-1.0.0.vsix
```

### 3. **Start WRE WebSocket Server**
```bash
# Navigate to WRE core
cd O:\Foundups-Agent

# Start WebSocket server for integration
python modules/wre_core/src/main.py --websocket

# Or with custom port
python modules/wre_core/src/main.py --websocket --ws-port 8765
```

### 4. **Use "Run WRE"**
1. Open any workspace in VS Code
2. Click 🚀 **WRE** button in status bar
3. Or use Command Palette: `Ctrl+Shift+P` → `WRE: Run WRE`
4. Watch 12-phase autonomous development flow

## Detailed Installation

### Prerequisites ✅

**Required:**
- VS Code 1.74.0+
- Python 3.8+
- Node.js 16+
- npm or yarn

**Verify Installation:**
```bash
# Check versions
code --version
python --version  
node --version
npm --version
```

### Extension Development Setup

**1. Clone and Setup:**
```bash
# Ensure you have the Foundups-Agent repo
cd O:\Foundups-Agent\extensions\claude_wre

# Install dependencies
npm install

# Install additional dev tools
npm install -g vsce  # VS Code Extension Manager
npm install -g typescript  # TypeScript compiler
```

**2. Development Dependencies:**
```json
{
  "@types/node": "18.x",
  "@types/vscode": "^1.74.0", 
  "@types/ws": "^8.5.0",
  "typescript": "^4.9.0",
  "ws": "^8.14.0"
}
```

**3. Compile Extension:**
```bash
# Compile TypeScript to JavaScript
npm run compile

# Watch mode for development
npm run watch
```

**4. Test Extension:**
```bash
# Open in Extension Development Host
# From extensions/claude_wre directory in VS Code, press F5
# This opens a new VS Code window with the extension loaded
```

### WRE Backend Setup

**1. Verify WRE Installation:**
```bash
cd O:\Foundups-Agent

# Test WRE directly
python modules/wre_core/src/main.py --help

# Should show WRE options including --websocket
```

**2. Install WebSocket Dependencies:**
```bash
# Install required Python packages
pip install websockets
pip install asyncio  # Usually built-in with Python 3.7+
```

**3. Test WebSocket Server:**
```bash
# Start WebSocket server
python modules/wre_core/src/main.py --websocket

# Should show:
# 🌐 Starting WRE WebSocket server on localhost:8765
# ✅ WRE WebSocket server started successfully  
# 🔗 Claude Code extensions can connect to ws://localhost:8765
```

### Integration Testing

**1. Test WebSocket Connection:**
```bash
# In browser console or WebSocket client:
const ws = new WebSocket('ws://localhost:8765');
ws.onmessage = (event) => console.log('Received:', event.data);
ws.send(JSON.stringify({ type: 'get_status' }));
```

**2. Test Extension Commands:**
- Open Command Palette (`Ctrl+Shift+P`)
- Type `WRE:` to see all WRE commands
- Try `WRE: Run WRE` and `WRE: WRE Status`

**3. Test Status Bar Integration:**
- Look for 🚀 **WRE Ready** in status bar (bottom right)
- Click to trigger WRE execution
- Status should update to show progress

### Package Extension for Distribution

**1. Create Extension Package:**
```bash
cd O:\Foundups-Agent\extensions\claude_wre

# Package extension
vsce package

# Creates: claude-wre-integration-1.0.0.vsix
```

**2. Install Packaged Extension:**
```bash
# Install in VS Code
code --install-extension claude-wre-integration-1.0.0.vsix

# Or through VS Code UI:
# Extensions → ... → Install from VSIX
```

**3. Distribute:**
- Share the `.vsix` file
- Or publish to VS Code Marketplace
- Or include in Foundups-Agent setup

## Configuration

### Extension Settings

Add to VS Code `settings.json`:
```json
{
  "claude-wre.autoStart": false,
  "claude-wre.defaultMode": "autonomous", 
  "claude-wre.quantumState": "0102",
  "claude-wre.wspCompliance": "strict",
  "claude-wre.websocketPort": 8765,
  "claude-wre.showStatusBar": true
}
```

### WRE Server Configuration

**Environment Variables:**
```bash
# Optional environment configuration
export WRE_WEBSOCKET_HOST=localhost
export WRE_WEBSOCKET_PORT=8765
export WRE_LOG_LEVEL=INFO
```

**Launch Arguments:**
```bash
# Full configuration
python modules/wre_core/src/main.py \
  --websocket \
  --ws-port 8765 \
  --directive "Default Claude Code session"
```

## Usage Workflows

### Basic Workflow
1. **Start WRE Server**: `python modules/wre_core/src/main.py --websocket`
2. **Open VS Code**: With any workspace
3. **Run WRE**: Click status bar or use Command Palette
4. **Monitor Progress**: Real-time updates in status and logs

### Development Workflow  
1. **Extension Development**: Use F5 for Extension Development Host
2. **Backend Changes**: Restart WebSocket server after changes
3. **Frontend Changes**: Reload Extension Development Host
4. **Testing**: Use both modes together for full integration testing

### Production Workflow
1. **Install Extension**: Via .vsix package
2. **Auto-start Server**: Configure WRE to start with system
3. **Seamless Operation**: WRE operates as transparent Claude Code skin

## Troubleshooting

### Common Issues

**"Extension not found"**
```bash
# Ensure proper compilation
npm run compile

# Check for TypeScript errors  
tsc --noEmit
```

**"WebSocket connection failed"**
```bash
# Verify server is running
python modules/wre_core/src/main.py --websocket

# Check port availability
netstat -an | grep :8765
```

**"WRE command failed"**
```bash
# Test WRE directly
python modules/wre_core/src/main.py --directive "Test session"

# Check Python path and dependencies
python -c "import websockets; print('WebSocket support OK')"
```

**"No workspace folder open"**
- Open a folder in VS Code before running WRE
- WRE requires workspace context for proper operation

### Debug Logging

**Extension Logs:**
- `View → Output → WRE Integration`

**WRE Server Logs:**
- `O:\Foundups-Agent\modules\wre_core\logs\websocket_server.log`

**VS Code Developer Tools:**
- `Help → Toggle Developer Tools`
- Check Console for extension errors

## Advanced Configuration

### Custom WebSocket Implementation

Extend `wre_integration.ts` for custom communication:
```typescript
// Add custom message handlers
private async handleCustomMessage(message: any) {
    switch(message.type) {
        case 'custom_command':
            await this.handleCustomCommand(message.data);
            break;
    }
}
```

### Multi-Workspace Support
- Extension supports multiple workspaces
- Each workspace can have its own WRE session
- Shared WebSocket server manages all sessions

### Performance Optimization
- WebSocket connection pooling
- Background server threading  
- Efficient status updates
- Memory management for long sessions

---

**Next Steps:**
1. Complete installation following this guide
2. Test basic "Run WRE" functionality
3. Verify WebSocket communication
4. Test 12-phase autonomous flow
5. Configure for daily development use

**Support:**
- File issues in Foundups-Agent repository
- Check WebSocket server logs for connection issues
- Use VS Code Developer Tools for extension debugging