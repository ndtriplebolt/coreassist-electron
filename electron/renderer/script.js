// CoreAssist Electron App Frontend
class CoreAssistApp {
    constructor() {
        this.isConnected = false;
        this.isListening = false;
        this.backendConfig = null;
        
        this.init();
    }

    async init() {
        // Load backend configuration
        await this.loadBackendConfig();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load app version
        await this.loadAppVersion();
        
        // Check connection status
        this.checkConnectionStatus();
        
        console.log('CoreAssist App initialized');
    }

    async loadBackendConfig() {
        try {
            this.backendConfig = await window.electronAPI.getBackendConfig();
            
            // Update UI with backend URLs
            document.getElementById('authServiceUrl').textContent = this.backendConfig.authService;
            document.getElementById('apiServiceUrl').textContent = this.backendConfig.apiService;
        } catch (error) {
            console.error('Failed to load backend config:', error);
            this.showError('Failed to load backend configuration');
        }
    }

    async loadAppVersion() {
        try {
            const version = await window.electronAPI.getVersion();
            document.getElementById('version').textContent = `v${version}`;
        } catch (error) {
            console.error('Failed to load app version:', error);
        }
    }

    setupEventListeners() {
        // Connect button
        document.getElementById('connectBtn').addEventListener('click', () => {
            this.connectToBackend();
        });

        // Settings button
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.openSettings();
        });

        // Voice button
        document.getElementById('voiceBtn').addEventListener('click', () => {
            this.toggleVoiceListening();
        });

        // Manage services button
        document.getElementById('manageServicesBtn').addEventListener('click', () => {
            this.openServiceManagement();
        });
    }

    async connectToBackend() {
        const connectBtn = document.getElementById('connectBtn');
        const statusElement = document.getElementById('connectionStatus');
        
        connectBtn.disabled = true;
        connectBtn.innerHTML = '<span class="btn-icon">⏳</span> Connecting...';
        statusElement.textContent = 'Connecting...';
        statusElement.className = 'status connecting';

        try {
            // Test connection to auth service
            const response = await fetch(`${this.backendConfig.authService}/health`, {
                method: 'GET',
                mode: 'cors'
            });

            if (response.ok) {
                this.isConnected = true;
                this.showDashboard();
                statusElement.textContent = 'Connected';
                statusElement.className = 'status connected';
                this.addActivity('Connected to CoreAssist backend');
            } else {
                throw new Error('Backend health check failed');
            }
        } catch (error) {
            console.error('Connection failed:', error);
            this.showError('Failed to connect to CoreAssist backend. Please check if the services are running.');
            statusElement.textContent = 'Connection failed';
            statusElement.className = 'status disconnected';
        } finally {
            connectBtn.disabled = false;
            connectBtn.innerHTML = '<span class="btn-icon">🔗</span> Connect to CoreAssist';
        }
    }

    showDashboard() {
        document.getElementById('authSection').style.display = 'none';
        document.getElementById('dashboardSection').style.display = 'block';
        
        // Load connected services
        this.loadConnectedServices();
    }

    async loadConnectedServices() {
        try {
            // This will eventually call your backend to get user's connected services
            // For now, we'll simulate the check
            const services = ['Google Tasks', 'Google Calendar', 'Slack'];
            
            services.forEach(serviceName => {
                // In a real implementation, you'd check the actual connection status
                this.updateServiceStatus(serviceName, false);
            });
        } catch (error) {
            console.error('Failed to load connected services:', error);
        }
    }

    updateServiceStatus(serviceName, isConnected) {
        const serviceItems = document.querySelectorAll('.service-item');
        serviceItems.forEach(item => {
            const nameElement = item.querySelector('.service-name');
            const statusElement = item.querySelector('.service-status');
            
            if (nameElement.textContent === serviceName) {
                statusElement.textContent = isConnected ? 'Connected' : 'Disconnected';
                statusElement.className = `service-status ${isConnected ? 'connected' : 'disconnected'}`;
            }
        });
    }

    toggleVoiceListening() {
        const voiceBtn = document.getElementById('voiceBtn');
        const voiceStatus = document.getElementById('voiceStatus');
        
        if (!this.isListening) {
            // Start listening
            this.isListening = true;
            voiceBtn.innerHTML = '<span class="btn-icon">🛑</span> Stop Listening';
            voiceBtn.className = 'btn btn-voice listening';
            voiceStatus.textContent = 'Listening for commands...';
            
            this.addActivity('Started voice listening');
            
            // TODO: Implement actual voice recognition
            console.log('Voice listening started');
            
        } else {
            // Stop listening
            this.isListening = false;
            voiceBtn.innerHTML = '<span class="btn-icon">🎤</span> Start Listening';
            voiceBtn.className = 'btn btn-voice';
            voiceStatus.textContent = 'Ready to listen';
            
            this.addActivity('Stopped voice listening');
            
            console.log('Voice listening stopped');
        }
    }

    openServiceManagement() {
        if (this.backendConfig) {
            // Open the backend dashboard in default browser
            const dashboardUrl = `${this.backendConfig.authService}/dashboard`;
            
            // Use Electron's shell to open external URL
            console.log('Opening service management:', dashboardUrl);
            
            // For now, just show a message
            this.showInfo(`Service management will open in your browser: ${dashboardUrl}`);
            this.addActivity('Opened service management');
        }
    }

    openSettings() {
        // TODO: Implement settings dialog
        this.showInfo('Settings panel coming soon!');
        console.log('Settings opened');
    }

    checkConnectionStatus() {
        if (!this.backendConfig) return;

        // Periodically check connection status
        setInterval(async () => {
            if (this.isConnected) {
                try {
                    const response = await fetch(`${this.backendConfig.authService}/health`, {
                        method: 'GET',
                        mode: 'cors'
                    });
                    
                    if (!response.ok) {
                        throw new Error('Health check failed');
                    }
                } catch (error) {
                    console.error('Lost connection to backend:', error);
                    this.isConnected = false;
                    document.getElementById('connectionStatus').textContent = 'Disconnected';
                    document.getElementById('connectionStatus').className = 'status disconnected';
                    this.addActivity('Lost connection to backend');
                }
            }
        }, 30000); // Check every 30 seconds
    }

    addActivity(text) {
        const activityList = document.getElementById('activityList');
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        
        activityItem.innerHTML = `
            <span class="activity-text">${text}</span>
            <span class="activity-time">${timeString}</span>
        `;
        
        activityList.insertBefore(activityItem, activityList.firstChild);
        
        // Keep only the last 10 activities
        while (activityList.children.length > 10) {
            activityList.removeChild(activityList.lastChild);
        }
    }

    showError(message) {
        // TODO: Implement proper error notifications
        console.error(message);
        alert(`Error: ${message}`);
    }

    showInfo(message) {
        // TODO: Implement proper info notifications
        console.info(message);
        alert(`Info: ${message}`);
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CoreAssistApp();
});