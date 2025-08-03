# QiLife App Installation Guide

## 📦 Package Contents

This installer contains:
- **electron-app/** - The main Electron application
- **python-backend.zip** - Python backend (compressed)
- **README.md** - This installation guide

## 🚀 Installation Steps

### 1. Extract the Installer
Extract `qilife-installer.zip` to your desired installation directory.

### 2. Install Python Backend

#### Windows:
```bash
# Extract the Python backend
cd qilife-installer
tar -xf python-backend.zip

# Install Python dependencies
cd python-backend
pip install -r requirements.txt

# Start the Python backend server
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

#### macOS/Linux:
```bash
# Extract the Python backend
cd qilife-installer
unzip python-backend.zip

# Install Python dependencies
cd python-backend
pip3 install -r requirements.txt

# Start the Python backend server
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 3. Start the Electron App

#### Windows:
```bash
cd electron-app
QiLife One.exe
```

#### macOS:
```bash
cd electron-app
open "QiLife One.app"
```

#### Linux:
```bash
cd electron-app
./QiLife\ One
```

## 🔧 Configuration

### API Configuration
The Electron app will automatically connect to the Python backend at:
- **URL**: `http://127.0.0.1:8000`
- **Port**: `8000`

### Environment Variables
Set these environment variables if needed:
```bash
export QILIFE_API_URL=http://127.0.0.1:8000
export QILIFE_DEBUG=true
```

## 🐛 Troubleshooting

### Python Backend Issues
1. **Port already in use**: Change the port in the uvicorn command
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Python version**: Ensure Python 3.8+ is installed

### Electron App Issues
1. **App won't start**: Check if Python backend is running
2. **Connection errors**: Verify API URL in app settings
3. **Permission issues**: Run as administrator (Windows) or with sudo (Linux)

## 📞 Support

For technical support, contact:
- **Email**: support@qilife.com
- **Documentation**: https://docs.qilife.com

## 🔄 Updates

To update the application:
1. Stop both the Python backend and Electron app
2. Replace the files with the new version
3. Restart both services

---
**QiLife App v0.1.0** - Built with ❤️ for productivity 