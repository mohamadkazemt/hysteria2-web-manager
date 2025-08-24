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
    mkdir -p src static docs scripts logs
    
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

# Copy application files
copy_files() {
    print_status "Copying application files..."
    
    # Copy source files if they exist
    if [ -f "app.py" ]; then
        cp app.py /opt/hysteria-web/src/
    fi
    
    if [ -d "templates" ]; then
        cp -r templates /opt/hysteria-web/src/
    fi
    
    if [ -f "requirements.txt" ]; then
        cp requirements.txt /opt/hysteria-web/
    fi
    
    print_success "Application files copied"
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
    
    # Enable UFW if not already enabled
    ufw --force enable
    
    # Allow SSH
    ufw allow ssh
    
    # Allow web interface port
    ufw allow 8080/tcp
    
    print_success "Firewall configured"
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

# Main installation function
main() {
    print_status "Starting Hysteria2 Web Manager installation..."
    
    check_root
    install_dependencies
    create_directories
    setup_python_env
    copy_files
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
    print_warning "Don't forget to configure your Hysteria2 clients through the web interface!"
}

# Run main function
main "$@"
