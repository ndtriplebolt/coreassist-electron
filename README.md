# CoreAssist Voice Agent

A secure, multi-user voice agent system with personal account connections for teams.

## Features

- **Personal Account Security**: Each user connects their own Google, Slack, and calendar accounts
- **Voice-First Interface**: Natural voice commands across all connected services  
- **Multi-Service Integration**: Google Tasks, Google Calendar, and Slack with more coming
- **Enterprise Security**: OAuth2 authentication and encrypted credential storage
- **Cross-Platform**: Native desktop applications for Windows, macOS, and Linux

## Architecture

This repository contains:

- **`/electron/`** - Electron desktop application
- **`/backend/`** - FastAPI backend with connector system
- **`/web/`** - Landing page and web assets
- **`/docs/`** - Documentation and guides

## Quick Start

### Desktop App Development
```bash
cd electron
npm install
npm start
```

### Backend Services  
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Landing Page
```bash
cd web
python -m http.server 3000
```

## Distribution

See `docs/electron-distribution-guide.md` for complete build and distribution instructions including:
- Code signing setup
- GitHub Actions CI/CD
- Cross-platform releases
- Auto-update implementation

## Security

- OAuth2 authentication for all external services
- Per-user credential isolation  
- Code-signed desktop applications
- Encrypted data storage

## License

Private - All rights reserved