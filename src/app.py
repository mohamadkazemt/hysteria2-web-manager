#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hysteria2 Complete Management Web Service
وب سرویس مدیریت کامل هیستریا

A Flask web application to view logs, manage clients and servers
"""

from flask import Flask, render_template, jsonify, request, Response
import os
import json
import subprocess
import time
from datetime import datetime, timedelta
import re
from threading import Thread
import socket
import yaml
import secrets
import string
import urllib.request
import ssl

app = Flask(__name__, template_folder="templates")

# Configuration
LOG_FILE = "/var/log/hysteria-monitor.log"
PORT = 8080
HOST = "0.0.0.0"  # Listen on all interfaces
MAX_LOG_LINES = 1000
HYSTERIA_DIR = "/etc/hysteria"
CLIENTS_CONFIG_FILE = "/opt/hysteria-web/clients.json"
SERVER_CONFIG_FILE = "/opt/hysteria-web/server.json"
HYSTERIA_BINARY = "/usr/local/bin/hysteria"

class HysteriaServerManager:
    def __init__(self):
        self.server_config_file = SERVER_CONFIG_FILE
        self.load_server_config()
    
    def load_server_config(self):
        """Load server configuration"""
        try:
            if os.path.exists(self.server_config_file):
                with open(self.server_config_file, 'r', encoding='utf-8') as f:
                    self.server_config = json.load(f)
            else:
                self.server_config = {
                    "installed": False,
                    "configured": False,
                    "running": False,
                    "port": 443,
                    "password": "",
                    "domain": "",
                    "config_file": "/etc/hysteria/server.yaml"
                }
                self.save_server_config()
        except Exception as e:
            print(f"Error loading server config: {e}")
            self.server_config = {}
    
    def save_server_config(self):
        """Save server configuration"""
        try:
            with open(self.server_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.server_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving server config: {e}")
    
    def check_hysteria_installed(self):
        """Check if Hysteria2 is installed"""
        try:
            result = subprocess.run([HYSTERIA_BINARY, 'version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def install_hysteria(self):
        """Install Hysteria2 binary"""
        try:
            # Download and install Hysteria2
            result = subprocess.run([
                '/usr/bin/bash', '-c',
                '/usr/bin/curl -fsSL https://get.hy2.sh/ | /usr/bin/bash'
            ], capture_output=True, text=True, timeout=300, 
               env={**os.environ, 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'})
            
            if result.returncode == 0:
                return {"success": True, "message": "Hysteria2 installed successfully"}
            else:
                return {"success": False, "error": f"Installation failed: {result.stderr}"}
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Installation timed out"}
        except Exception as e:
            return {"success": False, "error": f"Installation error: {str(e)}"}
    
    def generate_server_password(self):
        """Generate random server password"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    def get_server_ip(self):
        """Get server public IP"""
        try:
            # Try multiple IP detection services
            services = [
                'http://ifconfig.me',
                'http://ipecho.net/plain',
                'http://icanhazip.com'
            ]
            
            for service in services:
                try:
                    with urllib.request.urlopen(service, timeout=5) as response:
                        ip = response.read().decode().strip()
                        if self.validate_ip(ip):
                            return ip
                except:
                    continue
            
            return None
        except:
            return None
    
    def validate_ip(self, ip):
        """Validate IP address"""
        try:
            socket.inet_aton(ip)
            return True
        except:
            return False
    
    def generate_self_signed_cert(self, domain):
        """Generate self-signed SSL certificate"""
        try:
            cert_dir = "/etc/hysteria/certs"
            os.makedirs(cert_dir, exist_ok=True)
            
            cert_file = f"{cert_dir}/cert.pem"
            key_file = f"{cert_dir}/key.pem"
            
            # Generate self-signed certificate
            result = subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
                '-keyout', key_file, '-out', cert_file,
                '-days', '365', '-nodes',
                '-subj', f'/CN={domain}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "cert_file": cert_file,
                    "key_file": key_file
                }
            else:
                return {"success": False, "error": f"Certificate generation failed: {result.stderr}"}
        
        except Exception as e:
            return {"success": False, "error": f"Certificate error: {str(e)}"}
    
    def create_server_config(self, port, password, domain=None):
        """Create Hysteria2 server configuration"""
        server_ip = self.get_server_ip()
        
        if domain:
            # Generate self-signed certificate for domain
            cert_result = self.generate_self_signed_cert(domain)
            if not cert_result["success"]:
                return cert_result
            
            tls_config = f"""
  cert: {cert_result["cert_file"]}
  key: {cert_result["key_file"]}"""
        else:
            # Use self-signed certificate with IP
            cert_result = self.generate_self_signed_cert(server_ip or "hysteria-server")
            if not cert_result["success"]:
                return cert_result
            
            tls_config = f"""
  cert: {cert_result["cert_file"]}
  key: {cert_result["key_file"]}"""
        
        config = f"""# Hysteria2 Server Configuration
# Auto-generated server configuration

listen: :{port}
auth:
  type: password
  password: {password}

tls:{tls_config}

# QUIC optimizations
quic:
  initStreamReceiveWindow: 67108864
  maxStreamReceiveWindow: 67108864
  initConnReceiveWindow: 134217728
  maxConnReceiveWindow: 134217728
  maxIncomingStreams: 4096
  disablePathMTUDiscovery: false
  keepAlivePeriod: 10s
  handshakeIdleTimeout: 10s
  maxIncomingUniStreams: 4096

# Advanced settings
bandwidth:
  up: 1 gbps
  down: 1 gbps

# Enable UDP relay
relay:
  disable: false

# Obfuscation - Salamander
obfs:
  type: salamander
  salamander:
    password: {password}

# Logging
log:
  level: warn
  file: /var/log/hysteria-server.log

# Block some common ports for security
blockList:
  - "25"
  - "465"
  - "587"

# Masquerade
masquerade:
  type: proxy
  proxy:
    url: https://www.bing.com
    rewriteHost: true
"""
        return {"success": True, "config": config}
    
    def setup_server(self, port, password, domain=None):
        """Set up Hysteria2 server"""
        try:
            # Check if Hysteria is installed
            if not self.check_hysteria_installed():
                install_result = self.install_hysteria()
                if not install_result["success"]:
                    return install_result
            
            # Create server configuration
            config_result = self.create_server_config(port, password, domain)
            if not config_result["success"]:
                return config_result
            
            config_file = "/etc/hysteria/server.yaml"
            
            # Write configuration file
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_result["config"])
            
            # Create systemd service for server
            service_content = f"""[Unit]
Description=Hysteria2 Server
After=network.target

[Service]
Type=simple
ExecStart={HYSTERIA_BINARY} server --config {config_file}
Restart=on-failure
RestartSec=5
User=root
Group=root

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/log
ReadWritePaths=/etc/hysteria
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

[Install]
WantedBy=multi-user.target
"""
            
            service_file = "/etc/systemd/system/hysteria-server.service"
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(service_content)
            
            # Update server configuration
            self.server_config.update({
                "installed": True,
                "configured": True,
                "port": port,
                "password": password,
                "domain": domain or self.get_server_ip(),
                "config_file": config_file
            })
            self.save_server_config()
            
            # Reload systemd and start server
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            subprocess.run(['systemctl', 'enable', 'hysteria-server'], check=True)
            subprocess.run(['systemctl', 'start', 'hysteria-server'], check=True)
            
            return {
                "success": True,
                "message": "Hysteria2 server configured and started successfully",
                "server_info": {
                    "ip": self.get_server_ip(),
                    "port": port,
                    "password": password,
                    "domain": domain
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Server setup failed: {str(e)}"}
    
    def get_server_status(self):
        """Get server status"""
        try:
            # Check if installed
            installed = self.check_hysteria_installed()
            
            # Check if service is running
            result = subprocess.run(['systemctl', 'is-active', 'hysteria-server'], 
                                  capture_output=True, text=True)
            running = result.returncode == 0
            
            # Check if configured
            configured = os.path.exists("/etc/hysteria/server.yaml")
            
            return {
                "installed": installed,
                "configured": configured,
                "running": running,
                "config": self.server_config
            }
        except Exception as e:
            return {
                "installed": False,
                "configured": False,
                "running": False,
                "error": str(e)
            }

class HysteriaClientManager:
    def __init__(self):
        self.clients_file = CLIENTS_CONFIG_FILE
        self.load_clients()
    
    def load_clients(self):
        """Load clients from configuration file"""
        try:
            if os.path.exists(self.clients_file):
                with open(self.clients_file, 'r', encoding='utf-8') as f:
                    self.clients = json.load(f)
            else:
                # Default clients (existing ones)
                self.clients = {
                    "client1": {
                        "name": "Client1 (138.197.130.170)",
                        "server": "138.197.130.170:443",
                        "port": 1090,
                        "service": "hysteria-client",
                        "config_file": "/etc/hysteria/client.yaml",
                        "status": "unknown",
                        "password": "pass1234"
                    },
                    "client2": {
                        "name": "Client2 (185.55.241.111)", 
                        "server": "185.55.241.111:443",
                        "port": 1080,
                        "service": "hysteria-client2",
                        "config_file": "/etc/hysteria/client2.yaml",
                        "status": "unknown",
                        "password": "pass1234"
                    }
                }
                self.save_clients()
        except Exception as e:
            print(f"Error loading clients: {e}")
            self.clients = {}
    
    def save_clients(self):
        """Save clients to configuration file"""
        try:
            with open(self.clients_file, 'w', encoding='utf-8') as f:
                json.dump(self.clients, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving clients: {e}")
    
    def get_next_available_port(self):
        """Get next available SOCKS5 port"""
        used_ports = [client["port"] for client in self.clients.values()]
        for port in range(1081, 1100):
            if port not in used_ports:
                return port
        return 1081  # fallback
    
    def get_next_client_id(self):
        """Get next available client ID"""
        existing_nums = []
        for client_id in self.clients.keys():
            if client_id.startswith("client"):
                try:
                    num = int(client_id.replace("client", ""))
                    existing_nums.append(num)
                except:
                    pass
        
        for i in range(1, 100):
            if i not in existing_nums:
                return f"client{i}"
        return "client99"  # fallback
    
    def generate_password(self):
        """Generate random password"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    def create_client_config(self, server_ip, server_port, socks_port, password):
        """Create Hysteria2 client configuration"""
        config = f"""# Hysteria2 Client Configuration
# Auto-generated configuration
server: {server_ip}:{server_port}
auth: {password}

# تنظیمات QUIC حداکثری
quic:
  initStreamReceiveWindow: 67108864
  maxStreamReceiveWindow: 67108864  
  initConnReceiveWindow: 134217728
  maxConnReceiveWindow: 134217728
  maxIdleTimeout: 120s
  maxIncomingStreams: 4096
  disablePathMTUDiscovery: false
  keepAlivePeriod: 10s
  handshakeIdleTimeout: 10s
  maxIncomingUniStreams: 4096

# حداکثر بهینه‌سازی اتصال  
fastOpen: true
lazy: false

# Obfuscation - Salamander
obfs:
  type: salamander
  salamander:
    password: {password}

# SOCKS5 با بهینه‌سازی کامل
socks5:
  listen: 127.0.0.1:{socks_port}
  disableUDP: false

# TLS optimizations
tls:
  sni: cloudflare.com
  insecure: true
  serverName: cloudflare.com

# تنظیمات پیشرفته transport
transport:
  congestionControl: bbr
  
# بهینه‌سازی‌های اضافی
tcpKeepAlive: 10s
tcpNoDelay: true
tcpUserTimeout: 30s

# حداکثر buffer sizes  
socksOutboundBufferSize: 262144

# تنظیمات resolver
resolver:
  type: https
  https:
    addr: 1.1.1.1:443
    timeout: 10s

# Log level برای performance
log:
  level: warn
"""
        return config
    
    def create_systemd_service(self, client_id, config_file):
        """Create systemd service file"""
        service_content = f"""[Unit]
Description=Hysteria2 Client {client_id}
After=network.target

[Service]
Type=simple
ExecStart={HYSTERIA_BINARY} client --config {config_file}
Restart=on-failure
RestartSec=5
User=nobody
Group=nogroup

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/hysteria
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

[Install]
WantedBy=multi-user.target
"""
        return service_content
    
    def add_client(self, server_ip, server_port, password, custom_port=None):
        """Add a new Hysteria2 client"""
        try:
            # Get next available identifiers
            client_id = self.get_next_client_id()
            socks_port = custom_port if custom_port else self.get_next_available_port()
            service_name = f"hysteria-{client_id}"
            config_file = f"{HYSTERIA_DIR}/{client_id}.yaml"
            
            # Create client configuration
            config_content = self.create_client_config(server_ip, server_port, socks_port, password)
            
            # Write configuration file
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # Create systemd service
            service_file = f"/etc/systemd/system/{service_name}.service"
            service_content = self.create_systemd_service(client_id, config_file)
            
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(service_content)
            
            # Add to clients list
            self.clients[client_id] = {
                "name": f"Client {client_id} ({server_ip})",
                "server": f"{server_ip}:{server_port}",
                "port": socks_port,
                "service": service_name,
                "config_file": config_file,
                "status": "unknown",
                "password": password
            }
            
            # Save clients configuration
            self.save_clients()
            
            # Reload systemd and start service
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            subprocess.run(['systemctl', 'enable', service_name], check=True)
            subprocess.run(['systemctl', 'start', service_name], check=True)
            
            return {
                "success": True,
                "client_id": client_id,
                "socks_port": socks_port,
                "message": f"Client {client_id} created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def remove_client(self, client_id):
        """Remove a Hysteria2 client"""
        try:
            if client_id not in self.clients:
                return {"success": False, "error": "Client not found"}
            
            client = self.clients[client_id]
            service_name = client["service"]
            config_file = client["config_file"]
            service_file = f"/etc/systemd/system/{service_name}.service"
            
            # Stop and disable service
            try:
                subprocess.run(['systemctl', 'stop', service_name], check=False)
                subprocess.run(['systemctl', 'disable', service_name], check=False)
            except:
                pass
            
            # Remove files
            try:
                if os.path.exists(config_file):
                    os.remove(config_file)
                if os.path.exists(service_file):
                    os.remove(service_file)
            except:
                pass
            
            # Remove from clients list
            del self.clients[client_id]
            self.save_clients()
            
            # Reload systemd
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            
            return {
                "success": True,
                "message": f"Client {client_id} removed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class HysteriaMonitor:
    def __init__(self):
        self.client_manager = HysteriaClientManager()
        self.server_manager = HysteriaServerManager()
    
    def get_service_status(self, service_name):
        """Get systemd service status"""
        try:
            result = subprocess.run(['systemctl', 'is-active', service_name], 
                                  capture_output=True, text=True)
            return "running" if result.returncode == 0 else "stopped"
        except:
            return "unknown"
    
    def test_proxy(self, port):
        """Test SOCKS5 proxy connectivity"""
        try:
            # Try to connect to the proxy port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_clients_status(self):
        """Get current status of all clients"""
        clients = self.client_manager.clients.copy()
        
        for client_id, client in clients.items():
            service_status = self.get_service_status(client["service"])
            proxy_status = self.test_proxy(client["port"])
            
            if service_status == "running" and proxy_status:
                client["status"] = "online"
            else:
                client["status"] = "offline"
        
        return clients
    
    def get_system_info(self):
        """Get system information"""
        try:
            # Get system uptime
            uptime = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
            
            # Get memory usage
            memory = subprocess.run(['free', '-h'], capture_output=True, text=True)
            
            return {
                "uptime": uptime.stdout.strip() if uptime.returncode == 0 else "Unknown",
                "memory": memory.stdout.split('\n')[1] if memory.returncode == 0 else "Unknown"
            }
        except:
            return {"uptime": "Unknown", "memory": "Unknown"}

monitor = HysteriaMonitor()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint for client status"""
    clients = monitor.get_clients_status()
    system_info = monitor.get_system_info()
    
    return jsonify({
        "clients": clients,
        "system": system_info,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/logs')
def api_logs():
    """API endpoint for log data"""
    lines = int(request.args.get('lines', 50))
    filter_text = request.args.get('filter', '').lower()
    
    try:
        if os.path.exists(LOG_FILE):
            # Read log file
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            # Get last N lines
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Filter lines if filter text provided
            if filter_text:
                recent_lines = [line for line in recent_lines if filter_text in line.lower()]
            
            # Parse and format logs
            formatted_logs = []
            for line in recent_lines:
                line = line.strip()
                if line:
                    # Extract timestamp and message
                    parts = line.split(' - ', 1)
                    if len(parts) == 2:
                        timestamp_str, message = parts
                        
                        # Determine log type based on message content
                        log_type = "info"
                        if "🟢" in message or "ONLINE" in message:
                            log_type = "success"
                        elif "🔴" in message or "OFFLINE" in message:
                            log_type = "error"
                        elif "⚠️" in message or "WARNING" in message or "WARN" in message:
                            log_type = "warning"
                        elif "🛑" in message or "ERROR" in message:
                            log_type = "error"
                        
                        formatted_logs.append({
                            "timestamp": timestamp_str,
                            "message": message,
                            "type": log_type,
                            "raw": line
                        })
            
            return jsonify({
                "logs": formatted_logs,
                "total_lines": len(all_lines),
                "filtered_lines": len(formatted_logs)
            })
        else:
            return jsonify({"error": "Log file not found", "logs": []})
    
    except Exception as e:
        return jsonify({"error": f"Error reading logs: {str(e)}", "logs": []})

@app.route('/api/logs/stream')
def stream_logs():
    """Server-Sent Events endpoint for real-time logs"""
    def generate():
        if not os.path.exists(LOG_FILE):
            yield "data: {\"error\": \"Log file not found\"}\n\n"
            return
        
        # Start from end of file
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            # Go to end of file
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    line = line.strip()
                    if line:
                        # Parse log line
                        parts = line.split(' - ', 1)
                        if len(parts) == 2:
                            timestamp_str, message = parts
                            
                            log_type = "info"
                            if "🟢" in message or "ONLINE" in message:
                                log_type = "success"
                            elif "🔴" in message or "OFFLINE" in message:
                                log_type = "error"
                            elif "⚠️" in message or "WARNING" in message:
                                log_type = "warning"
                            
                            log_data = {
                                "timestamp": timestamp_str,
                                "message": message,
                                "type": log_type,
                                "raw": line
                            }
                            
                            yield f"data: {json.dumps(log_data)}\n\n"
                else:
                    time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/restart/<client>')
def restart_client(client):
    """API endpoint to restart a client"""
    clients = monitor.client_manager.clients
    
    if client == 'monitor':
        service_name = 'hysteria-monitor'
    elif client == 'server':
        service_name = 'hysteria-server'
    elif client in clients:
        service_name = clients[client]["service"]
    else:
        return jsonify({"error": "Invalid client"}), 400
    
    try:
        # Restart service
        result = subprocess.run(['systemctl', 'restart', service_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({"success": f"{service_name} restarted successfully"})
        else:
            return jsonify({"error": f"Failed to restart {service_name}: {result.stderr}"}), 500
    
    except Exception as e:
        return jsonify({"error": f"Error restarting service: {str(e)}"}), 500

# Client management endpoints
@app.route('/api/clients', methods=['GET'])
def api_get_clients():
    """API endpoint to get all clients"""
    return jsonify(monitor.client_manager.clients)

@app.route('/api/clients', methods=['POST'])
def api_add_client():
    """API endpoint to add a new client"""
    try:
        data = request.get_json()
        
        # Validate required fields
        server_ip = data.get('server_ip', '').strip()
        server_port = data.get('server_port', 443)
        password = data.get('password', '').strip()
        custom_port = data.get('custom_port')
        
        if not server_ip:
            return jsonify({"error": "Server IP is required"}), 400
        
        if not password:
            password = monitor.client_manager.generate_password()
        
        # Validate server_port
        try:
            server_port = int(server_port)
            if not (1 <= server_port <= 65535):
                raise ValueError("Invalid port range")
        except:
            return jsonify({"error": "Invalid server port"}), 400
        
        # Validate custom_port if provided
        if custom_port:
            try:
                custom_port = int(custom_port)
                if not (1024 <= custom_port <= 65535):
                    raise ValueError("Custom port must be between 1024-65535")
                
                # Check if port is already in use
                used_ports = [client["port"] for client in monitor.client_manager.clients.values()]
                if custom_port in used_ports:
                    return jsonify({"error": "Port already in use"}), 400
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        
        # Add client
        result = monitor.client_manager.add_client(server_ip, server_port, password, custom_port)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({"error": f"Error adding client: {str(e)}"}), 500

@app.route('/api/clients/<client_id>', methods=['DELETE'])
def api_remove_client(client_id):
    """API endpoint to remove a client"""
    try:
        # Don't allow removing original clients
        if client_id in ['client1', 'client2']:
            return jsonify({"error": "Cannot remove default clients"}), 403
        
        result = monitor.client_manager.remove_client(client_id)
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({"error": f"Error removing client: {str(e)}"}), 500

# Server management endpoints
@app.route('/api/server/status', methods=['GET'])
def api_server_status():
    """API endpoint to get server status"""
    try:
        status = monitor.server_manager.get_server_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": f"Error getting server status: {str(e)}"}), 500

@app.route('/api/server/setup', methods=['POST'])
def api_setup_server():
    """API endpoint to set up Hysteria2 server"""
    try:
        data = request.get_json()
        
        port = data.get('port', 443)
        password = data.get('password', '').strip()
        domain = data.get('domain', '').strip()
        
        if not password:
            password = monitor.server_manager.generate_server_password()
        
        # Validate port
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                raise ValueError("Invalid port range")
        except:
            return jsonify({"error": "Invalid port"}), 400
        
        # Set up server
        result = monitor.server_manager.setup_server(port, password, domain or None)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({"error": f"Error setting up server: {str(e)}"}), 500

@app.route('/api/server/install', methods=['POST'])
def api_install_hysteria():
    """API endpoint to install Hysteria2"""
    try:
        result = monitor.server_manager.install_hysteria()
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({"error": f"Error installing Hysteria2: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Starting Hysteria2 Complete Management Web Service...")
    print(f"📊 Dashboard will be available at: http://localhost:{PORT}")
    print(f"🔗 External access: http://YOUR_SERVER_IP:{PORT}")
    print("=" * 50)
    
    # Ensure hysteria directory exists
    os.makedirs(HYSTERIA_DIR, exist_ok=True)
    
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
