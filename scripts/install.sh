#!/bin/bash

# Hysteria2 Web Manager Installation Script
# مدیریت وب هیستریا2 - اسکریپت نصب

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# GitHub repository info
REPO_URL="https://github.com/mohamadkazemt/hysteria2-web-manager"
RAW_URL="https://raw.githubusercontent.com/mohamadkazemt/hysteria2-web-manager/main"

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Install system dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    # Update package list
    apt update
    
    # Install required packages
    apt install -y python3 python3-pip python3-venv curl wget ufw
    
    print_success "System dependencies installed"
}

# Create project directory
create_directories() {
    print_status "Creating project directories..."
    
    # Create main directory
    mkdir -p /opt/hysteria-web
    cd /opt/hysteria-web
    
    # Create subdirectories
    mkdir -p src static docs scripts logs src/templates
    
    print_success "Directories created"
}

# Set up Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd /opt/hysteria-web
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install Python dependencies
    pip install flask pyyaml requests
    
    print_success "Python environment set up"
}

# Download application files from GitHub
download_files() {
    print_status "Downloading application files from GitHub..."
    
    cd /opt/hysteria-web
    
    # Download main application file
    curl -fsSL "${RAW_URL}/src/app.py" -o src/app.py
    chmod +x src/app.py
    
    # Download template file
    curl -fsSL "${RAW_URL}/src/templates/index.html" -o src/templates/index.html
    
    # Download requirements
    curl -fsSL "${RAW_URL}/requirements.txt" -o requirements.txt
    
    # Install Python dependencies from downloaded requirements
    source venv/bin/activate
    pip install -r requirements.txt
    
    print_success "Application files downloaded"
}

# Create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/hysteria-web.service << 'EOL'
[Unit]
Description=Hysteria2 Web Manager
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/hysteria-web
Environment=PATH=/opt/hysteria-web/venv/bin
ExecStart=/opt/hysteria-web/venv/bin/python3 /opt/hysteria-web/src/app.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hysteria-web

# Allow write access to hysteria configs
ReadWritePaths=/etc/hysteria
ReadWritePaths=/etc/systemd/system
ReadWritePaths=/var/log
ReadWritePaths=/opt/hysteria-web

[Install]
WantedBy=multi-user.target
EOL

    # Reload systemd
    systemctl daemon-reload
    systemctl enable hysteria-web
    
    print_success "Systemd service created"
}

# Configure firewall
configure_firewall() {
    print_status "Configuring firewall..."
    
    # Check if UFW is installed and enable it
    if command -v ufw > /dev/null; then
        # Enable UFW if not already enabled
        ufw --force enable
        
        # Allow SSH
        ufw allow ssh
        
        # Allow web interface port
        ufw allow 8080/tcp
        
        print_success "Firewall configured"
    else
        print_warning "UFW not found, skipping firewall configuration"
    fi
}

# Create management scripts
create_management_scripts() {
    print_status "Creating management scripts..."
    
    # Create monitor management script
    cat > /usr/local/bin/hysteria-manager << 'EOL'
#!/bin/bash

case "$1" in
    start)
        systemctl start hysteria-web
        echo "Hysteria2 Web Manager started"
        ;;
    stop)
        systemctl stop hysteria-web
        echo "Hysteria2 Web Manager stopped"
        ;;
    restart)
        systemctl restart hysteria-web
        echo "Hysteria2 Web Manager restarted"
        ;;
    status)
        systemctl status hysteria-web
        ;;
    logs)
        journalctl -u hysteria-web -f
        ;;
    enable)
        systemctl enable hysteria-web
        echo "Hysteria2 Web Manager enabled"
        ;;
    disable)
        systemctl disable hysteria-web
        echo "Hysteria2 Web Manager disabled"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable}"
        exit 1
        ;;
esac
EOL

    chmod +x /usr/local/bin/hysteria-manager
    
    print_success "Management scripts created"
}

# Create initial configuration files
create_config_files() {
    print_status "Creating initial configuration files..."
    
    cd /opt/hysteria-web
    
    # Create empty clients.json if it doesn't exist
    if [ ! -f clients.json ]; then
        echo '{}' > clients.json
    fi
    
    # Create empty server.json if it doesn't exist  
    if [ ! -f server.json ]; then
        echo '{}' > server.json
    fi
    
    # Set proper permissions
    chmod 644 clients.json server.json
    
    print_success "Configuration files created"
}

# Main installation function
main() {
    print_status "Starting Hysteria2 Web Manager installation..."
    echo "Repository: ${REPO_URL}"
    echo
    
    check_root
    install_dependencies
    create_directories
    setup_python_env
    download_files
    create_config_files
    create_systemd_service
    configure_firewall
    create_management_scripts
    
    print_success "Installation completed successfully!"
    echo
    print_status "You can now:"
    echo "  • Start the service: hysteria-manager start"
    echo "  • Check status: hysteria-manager status"
    echo "  • View logs: hysteria-manager logs"
    echo "  • Access web interface: http://YOUR_SERVER_IP:8080"
    echo
    print_status "GitHub Repository: ${REPO_URL}"
    print_warning "Don't forget to configure your Hysteria2 clients through the web interface!"
}

# Run main function
main "$@"
