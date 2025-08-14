# Startup Scripts for Wiko Cutlery Employee Assistant

## Automated Startup Scripts

### macOS Startup Script

Create `start_wiko_assistant.sh`:

```bash
#!/bin/bash

# Wiko Cutlery Employee Assistant Startup Script
# Save this file and make it executable: chmod +x start_wiko_assistant.sh

echo "🚀 Starting Wiko Cutlery Employee Assistant..."

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "📡 Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Start Backend
echo "🔧 Starting Flask backend..."
cd "$SCRIPT_DIR/wiko_chatbot"
source venv/bin/activate
python src/main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 10

# Start Frontend
echo "🎨 Starting React frontend..."
cd "$SCRIPT_DIR/wiko-chatbot-frontend"
npm run preview &
FRONTEND_PID=$!

echo "✅ Wiko Assistant is starting up..."
echo "🌐 Frontend will be available at: http://localhost:4173"
echo "🔧 Backend API available at: http://localhost:5000"
echo ""
echo "📋 Demo Accounts:"
echo "   Admin: admin / admin123"
echo "   Customer Service: customer_service / service123"
echo "   Sales: sales / sales123"
echo "   Manager: manager / manager123"
echo ""
echo "⏹️  To stop the application, press Ctrl+C"

# Wait for user to stop
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Keep script running
wait
```

### Quick Stop Script

Create `stop_wiko_assistant.sh`:

```bash
#!/bin/bash

echo "🛑 Stopping Wiko Cutlery Employee Assistant..."

# Kill Flask processes
pkill -f "python src/main.py"

# Kill Node/npm processes for the frontend
pkill -f "vite preview"

# Kill any remaining processes
pkill -f "wiko"

echo "✅ All services stopped"
```

### Development Mode Script

Create `start_development.sh`:

```bash
#!/bin/bash

echo "🔧 Starting Wiko Assistant in Development Mode..."

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "📡 Starting Ollama service..."
    ollama serve &
    sleep 5
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Start Backend in debug mode
echo "🔧 Starting Flask backend (debug mode)..."
cd "$SCRIPT_DIR/wiko_chatbot"
source venv/bin/activate
export FLASK_DEBUG=1
export USE_MOCK_SERVICES=true
python src/main.py &
BACKEND_PID=$!

sleep 10

# Start Frontend in development mode
echo "🎨 Starting React frontend (development mode)..."
cd "$SCRIPT_DIR/wiko-chatbot-frontend"
npm run dev &
FRONTEND_PID=$!

echo "✅ Development environment starting..."
echo "🌐 Frontend (dev): http://localhost:5173"
echo "🔧 Backend (debug): http://localhost:5000"
echo "⏹️  To stop, press Ctrl+C"

trap "echo '🛑 Stopping development services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
```

## Installation Instructions

1. **Save the scripts** in your `wiko-cutlery-assistant-final` directory
2. **Make them executable**:
   ```bash
   chmod +x start_wiko_assistant.sh
   chmod +x stop_wiko_assistant.sh
   chmod +x start_development.sh
   ```
3. **Run the startup script**:
   ```bash
   ./start_wiko_assistant.sh
   ```

## macOS Application Bundle (Optional)

Create a macOS app bundle for easier access:

### Create App Structure
```bash
mkdir -p "Wiko Assistant.app/Contents/MacOS"
mkdir -p "Wiko Assistant.app/Contents/Resources"
```

### Create Info.plist
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>wiko-assistant</string>
    <key>CFBundleIdentifier</key>
    <string>com.wiko.assistant</string>
    <key>CFBundleName</key>
    <string>Wiko Assistant</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>
```

### Create Launcher Script
Save as `Wiko Assistant.app/Contents/MacOS/wiko-assistant`:

```bash
#!/bin/bash
cd "$(dirname "$0")/../../.."
./start_wiko_assistant.sh
```

Make it executable:
```bash
chmod +x "Wiko Assistant.app/Contents/MacOS/wiko-assistant"
```

## Automatic Startup on Boot (Optional)

### Create LaunchAgent
Create `~/Library/LaunchAgents/com.wiko.assistant.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.wiko.assistant</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/your/start_wiko_assistant.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.wiko.assistant.plist
```

## Troubleshooting Scripts

### Health Check Script
Create `health_check.sh`:

```bash
#!/bin/bash

echo "🔍 Wiko Assistant Health Check"
echo "================================"

# Check Ollama
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama: Running"
else
    echo "❌ Ollama: Not running"
fi

# Check Backend
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Backend: Running (port 5000)"
else
    echo "❌ Backend: Not responding"
fi

# Check Frontend
if curl -s http://localhost:4173 > /dev/null; then
    echo "✅ Frontend: Running (port 4173)"
else
    echo "❌ Frontend: Not responding"
fi

# Check disk space
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    echo "✅ Disk Space: ${DISK_USAGE}% used"
else
    echo "⚠️  Disk Space: ${DISK_USAGE}% used (consider cleanup)"
fi

# Check memory
MEMORY_USAGE=$(ps aux | grep -E "(ollama|python|node)" | awk '{sum += $4} END {print sum}')
echo "📊 Memory Usage: ${MEMORY_USAGE}% (AI services)"

echo "================================"
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:4173"
echo "   Backend API: http://localhost:5000/api/health"
```

### Log Viewer Script
Create `view_logs.sh`:

```bash
#!/bin/bash

echo "📋 Wiko Assistant Logs"
echo "======================"

echo "🔧 Backend Logs (last 20 lines):"
echo "--------------------------------"
if [ -f "wiko_chatbot/logs/app.log" ]; then
    tail -20 wiko_chatbot/logs/app.log
else
    echo "No backend logs found"
fi

echo ""
echo "🎨 Frontend Logs (from browser console):"
echo "---------------------------------------"
echo "Open browser developer tools to view frontend logs"

echo ""
echo "📡 Ollama Logs:"
echo "---------------"
if command -v ollama &> /dev/null; then
    ollama ps
else
    echo "Ollama not found in PATH"
fi
```

Make all scripts executable:
```bash
chmod +x health_check.sh
chmod +x view_logs.sh
```

## Usage Tips

1. **Daily Use**: Run `./start_wiko_assistant.sh` each morning
2. **Development**: Use `./start_development.sh` for testing changes
3. **Health Monitoring**: Run `./health_check.sh` if issues occur
4. **Clean Shutdown**: Always use `./stop_wiko_assistant.sh` or Ctrl+C

These scripts make daily operation of the Wiko Assistant simple and reliable!

