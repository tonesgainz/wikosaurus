# Wiko Cutlery Employee Assistant - Quick Start Guide

**Get up and running in 30 minutes**

## Prerequisites Checklist

- [ ] macOS 12.0 or later
- [ ] 16GB RAM (8GB minimum)
- [ ] 20GB free disk space
- [ ] Admin privileges
- [ ] Internet connection for setup

## Step 1: Install Dependencies (10 minutes)

### Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Install Node.js and Python
```bash
brew install node python@3.11
```

### Verify installations
```bash
node --version  # Should be 18.0+
python3 --version  # Should be 3.9+
```

## Step 2: Install Ollama (5 minutes)

### Download and install Ollama
1. Visit https://ollama.ai/download
2. Download the macOS installer
3. Run the installer and follow prompts

### Install AI model
```bash
# For 16GB+ RAM systems (recommended)
ollama pull llama3:8b

# For 8-12GB RAM systems
ollama pull mistral:7b
```

## Step 3: Deploy Application (10 minutes)

### Extract application files
```bash
# Extract the provided application package to your desired location
cd /path/to/wiko-chatbot
```

### Setup Backend
```bash
cd wiko_chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/utils/init_db.py
```

### Setup Frontend
```bash
cd ../wiko-chatbot-frontend
npm install
npm run build
```

## Step 4: Start Services (5 minutes)

### Terminal 1 - Start Backend
```bash
cd wiko_chatbot
source venv/bin/activate
python src/main.py
```

### Terminal 2 - Start Frontend
```bash
cd wiko-chatbot-frontend
npm run preview
```

## Step 5: Access Application

1. Open browser to http://localhost:4173
2. Use demo accounts to login:
   - **Admin**: username `admin`, password `admin123`
   - **Customer Service**: username `customer_service`, password `service123`
   - **Sales**: username `sales`, password `sales123`
   - **Manager**: username `manager`, password `manager123`

## Quick Test

1. Login with admin account
2. Type: "Hello, can you help me with customer service?"
3. Switch to Translation tab
4. Type: "Translate 'Hello customer' to German"
5. Try PDF Analysis by uploading a document

## Troubleshooting

**Ollama not responding?**
```bash
ollama serve
```

**Frontend won't load?**
- Check if backend is running on port 5000
- Verify no firewall blocking ports 4173 and 5000

**Backend errors?**
- Ensure Python virtual environment is activated
- Check if database was initialized properly

## Next Steps

- Read the full Deployment Guide for detailed configuration
- Customize user accounts and permissions
- Configure organizational branding
- Set up automated startup scripts

## Support

For detailed troubleshooting and advanced configuration, refer to the complete Deployment Guide included with this package.

