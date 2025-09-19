# CoreAssist Electron App Distribution Guide

This guide walks you through building and distributing your CoreAssist Electron app with professional code signing and auto-updates.

## Prerequisites

### 1. Electron Project Setup
Ensure you have an Electron project with:
```json
// package.json
{
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "dist": "npm run build"
  }
}
```

### 2. Install electron-builder
```bash
npm install --save-dev electron-builder
```

## Step 1: Configure electron-builder

Add this configuration to your `package.json`:

```json
{
  "build": {
    "appId": "com.yourcompany.coreassist",
    "productName": "CoreAssist Voice Agent",
    "directories": {
      "output": "dist"
    },
    "files": [
      "build/**/*",
      "node_modules/**/*",
      "main.js",
      "package.json"
    ],
    "extraResources": [
      {
        "from": "assets/",
        "to": "assets/",
        "filter": ["**/*"]
      }
    ],
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        },
        {
          "target": "portable",
          "arch": ["x64"]
        }
      ],
      "icon": "build/icon.ico",
      "publisherName": "Your Company Name"
    },
    "mac": {
      "target": [
        {
          "target": "dmg",
          "arch": ["x64", "arm64"]
        }
      ],
      "icon": "build/icon.icns",
      "category": "public.app-category.productivity"
    },
    "linux": {
      "target": [
        {
          "target": "AppImage",
          "arch": ["x64"]
        },
        {
          "target": "deb",
          "arch": ["x64"]
        }
      ],
      "icon": "build/icon.png",
      "category": "Office"
    },
    "publish": {
      "provider": "github",
      "owner": "yourusername",
      "repo": "coreassist"
    }
  }
}
```

## Step 2: Create Application Icons

Create these icon files in a `build/` directory:

### Windows
- `build/icon.ico` (256x256 pixels, .ico format)

### macOS  
- `build/icon.icns` (1024x1024 pixels, .icns format)
- Use `png2icns` or online converters

### Linux
- `build/icon.png` (512x512 pixels, .png format)

## Step 3: Code Signing Setup

### Windows Code Signing

**Option A: Standard Code Signing Certificate**
1. Purchase certificate from DigiCert, Sectigo, or Comodo (~$100-300/year)
2. Set environment variables:
```bash
CSC_LINK=path/to/certificate.p12
CSC_KEY_PASSWORD=your_certificate_password
```

**Option B: Azure Trusted Signing (Recommended)**
1. Set up Azure Trusted Signing (~$10/month)
2. Configure environment:
```bash
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
AZURE_TRUSTED_SIGNING_ACCOUNT_NAME=your_account_name
AZURE_TRUSTED_SIGNING_CERTIFICATE_PROFILE_NAME=your_profile_name
```

### macOS Code Signing

1. Join Apple Developer Program ($99/year)
2. Create certificates in Keychain Access:
   - Developer ID Application
   - Developer ID Installer
3. Set environment variables:
```bash
CSC_NAME="Developer ID Application: Your Name (TEAM_ID)"
APPLE_ID=your_apple_id@example.com
APPLE_APP_SPECIFIC_PASSWORD=your_app_specific_password
```

## Step 4: Build Scripts

Add these scripts to `package.json`:

```json
{
  "scripts": {
    "build": "electron-builder",
    "build:win": "electron-builder --win",
    "build:mac": "electron-builder --mac",
    "build:linux": "electron-builder --linux",
    "build:all": "electron-builder --mac --win --linux",
    "publish": "electron-builder --publish always",
    "draft": "electron-builder --publish never"
  }
}
```

## Step 5: GitHub Actions CI/CD

Create `.github/workflows/build.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build Electron app
      run: npm run build
      env:
        CSC_LINK: ${{ secrets.CSC_LINK }}
        CSC_KEY_PASSWORD: ${{ secrets.CSC_KEY_PASSWORD }}
        APPLE_ID: ${{ secrets.APPLE_ID }}
        APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist-${{ matrix.os }}
        path: dist/
```

## Step 6: Auto-Update Implementation

### Install electron-updater
```bash
npm install electron-updater
```

### Add to main process (main.js)
```javascript
const { autoUpdater } = require('electron-updater');

// Check for updates
app.whenReady().then(() => {
  autoUpdater.checkForUpdatesAndNotify();
});

autoUpdater.on('update-available', () => {
  console.log('Update available');
});

autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall();
});
```

## Step 7: Release Process

### Manual Release
1. Build locally:
```bash
npm run build:all
```

2. Upload to GitHub Releases:
   - Go to GitHub → Releases → New Release
   - Upload files from `dist/` folder
   - Include these files:
     - `CoreAssist Setup 1.0.0.exe` (Windows)
     - `CoreAssist-1.0.0.dmg` (macOS)
     - `CoreAssist-1.0.0.AppImage` (Linux)
     - `latest.yml` (Windows updater)
     - `latest-mac.yml` (macOS updater)

### Automated Release
1. Create a git tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

2. GitHub Actions will automatically:
   - Build for all platforms
   - Code sign the executables
   - Create a GitHub release
   - Upload all distributables

## Step 8: Update Landing Page URLs

Update the download URLs in your `index.html`:

```javascript
const downloadUrls = {
  windows: 'https://github.com/yourusername/coreassist/releases/latest/download/CoreAssist-Setup.exe',
  mac: 'https://github.com/yourusername/coreassist/releases/latest/download/CoreAssist.dmg',
  linux: 'https://github.com/yourusername/coreassist/releases/latest/download/CoreAssist.AppImage'
};
```

## Cost Breakdown

### Required Certificates
- **Windows EV Code Signing**: ~$400/year (no warnings)
- **macOS Developer ID**: $99/year (Apple Developer Program)
- **Total**: ~$500/year for professional distribution

### Alternative (Budget Option)
- **Azure Trusted Signing**: ~$10/month ($120/year)
- **macOS Developer ID**: $99/year  
- **Total**: ~$220/year

### Hosting
- **GitHub Releases**: Free (unlimited for public repos)
- **CDN (optional)**: ~$5-20/month for faster downloads

## Testing Checklist

Before release, test on clean systems:

- [ ] Windows installer runs without warnings
- [ ] macOS app opens without Gatekeeper blocks
- [ ] Linux AppImage runs on Ubuntu/Fedora
- [ ] Auto-updater detects and installs updates
- [ ] All OAuth flows work correctly
- [ ] API connections to your backend succeed

## Security Best Practices

1. **Never commit certificates** to version control
2. **Use environment variables** for all secrets
3. **Test on isolated systems** before public release
4. **Monitor crash reports** with Sentry or similar
5. **Keep Electron updated** for security patches

## Deployment Timeline

- **Week 1**: Set up electron-builder and basic builds
- **Week 2**: Obtain and configure code signing certificates  
- **Week 3**: Set up GitHub Actions and auto-update
- **Week 4**: Test on all platforms and release v1.0.0

This process will give you professional-grade Electron app distribution with automatic updates and security trust across all platforms.