<div align="center">

# 🚀 Hysteria2 Web Manager
### مدیریت کامل وب هیستریا2

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-red.svg)](https://flask.palletsprojects.com)

[English](#english) | [فارسی](#فارسی)

</div>

## فارسی

### 📖 درباره پروژه

Hysteria2 Web Manager یک پنل مدیریت کامل و قدرتمند برای سرور و کلاینت‌های Hysteria2 است که با Flask پیاده‌سازی شده. این ابزار امکان مدیریت آسان و گرافیکی سرور و کلاینت‌های Hysteria2 را فراهم می‌کند.

### ✨ ویژگی‌های کلیدی

#### 🖥️ مدیریت سرور
- ✅ **نصب خودکار** سرور Hysteria2
- ✅ **پیکربندی آسان** با رابط گرافیکی
- ✅ **تولید خودکار** گواهی SSL
- ✅ **مدیریت سرویس** systemd
- ✅ **نظارت وضعیت** لحظه‌ای

#### 👥 مدیریت کلاینت‌ها
- ✅ **افزودن/حذف** کلاینت‌ها
- ✅ **پیکربندی SOCKS5** خودکار
- ✅ **نظارت وضعیت** کلاینت‌ها
- ✅ **راه‌اندازی مجدد** سرویس‌ها
- ✅ **تست اتصال** خودکار

#### 📊 نظارت و لاگ‌ها
- ✅ **لاگ‌های لحظه‌ای** با فیلتر
- ✅ **اطلاعات سیستم** (CPU, RAM, Network)
- ✅ **نمودارهای وضعیت** تعاملی
- ✅ **هشدارهای خودکار** در صورت مشکل

#### 🎨 رابط کاربری
- ✅ **طراحی ریسپانسیو** برای موبایل و دسکتاپ
- ✅ **پشتیبانی کامل** از زبان فارسی (RTL)
- ✅ **تم تیره/روشن**
- ✅ **انیمیشن‌های زیبا**

### 🛠️ نصب سریع

#### روش ۱: نصب خودکار (توصیه شده)

```bash
# دانلود و اجرای اسکریپت نصب
curl -fsSL https://raw.githubusercontent.com/mohamadkazemt/hysteria2-web-manager/main/scripts/install.sh | sudo bash

# یا
wget -O - https://raw.githubusercontent.com/mohamadkazemt/hysteria2-web-manager/main/scripts/install.sh | sudo bash
```

#### روش ۲: نصب دستی

```bash
# کلون کردن پروژه
git clone https://github.com/mohamadkazemt/hysteria2-web-manager.git
cd hysteria2-web-manager

# اجرای اسکریپت نصب
sudo bash scripts/install.sh
```

#### روش ۳: نصب از کد منبع

```bash
# وابستگی‌های سیستم
sudo apt update
sudo apt install -y python3 python3-pip python3-venv curl wget ufw

# کلون پروژه
git clone https://github.com/mohamadkazemt/hysteria2-web-manager.git
cd hysteria2-web-manager

# محیط مجازی Python
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌های Python
pip install -r requirements.txt

# کپی فایل‌ها
sudo mkdir -p /opt/hysteria-web
sudo cp -r src /opt/hysteria-web/
sudo cp -r scripts /opt/hysteria-web/
sudo cp requirements.txt /opt/hysteria-web/

# ساخت سرویس systemd
sudo cp scripts/hysteria-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hysteria-web
sudo systemctl start hysteria-web
```

### 🚀 راه‌اندازی

پس از نصب، سرویس را راه‌اندازی کنید:

```bash
# شروع سرویس
hysteria-manager start

# بررسی وضعیت
hysteria-manager status

# مشاهده لاگ‌ها
hysteria-manager logs
```

حالا به آدرس زیر بروید:
```
http://YOUR_SERVER_IP:8080
```

### 📋 دستورات مدیریت

```bash
hysteria-manager start      # شروع سرویس
hysteria-manager stop       # توقف سرویس  
hysteria-manager restart    # راه‌اندازی مجدد
hysteria-manager status     # وضعیت سرویس
hysteria-manager logs       # نمایش لاگ‌ها
hysteria-manager enable     # فعال‌سازی خودکار
hysteria-manager disable    # غیرفعال‌سازی خودکار
```

### 🔧 پیکربندی

#### تنظیمات فایروال

```bash
# اجازه دسترسی به پورت وب (8080)
sudo ufw allow 8080/tcp

# اجازه دسترسی به پورت Hysteria2 (443)
sudo ufw allow 443/tcp
```

#### تنظیمات پیشرفته

فایل پیکربندی در مسیر `/opt/hysteria-web/config.json`:

```json
{
    "web_port": 8080,
    "hysteria_port": 443,
    "log_level": "INFO",
    "max_clients": 50,
    "auto_restart": true
}
```

### 📱 استفاده از رابط وب

1. **مدیریت سرور**: نصب و پیکربندی سرور Hysteria2
2. **مدیریت کلاینت‌ها**: افزودن و حذف کلاینت‌ها
3. **نظارت لاگ‌ها**: مشاهده لاگ‌های لحظه‌ای
4. **وضعیت سیستم**: اطلاعات سیستم و شبکه

### 🛡️ امنیت

- 🔐 **احراز هویت** با رمز عبور
- 🚫 **محدودیت IP** برای دسترسی
- 📝 **لاگ کامل** تمام فعالیت‌ها
- 🔒 **رمزگذاری** اتصالات

### 📚 مستندات API

#### وضعیت سیستم
```bash
GET /api/status
```

#### مدیریت کلاینت‌ها
```bash
GET /api/clients          # لیست کلاینت‌ها
POST /api/clients         # افزودن کلاینت
DELETE /api/clients/{id}  # حذف کلاینت
```

#### مدیریت سرور
```bash
GET /api/server/status    # وضعیت سرور
POST /api/server/install  # نصب سرور
POST /api/server/setup    # پیکربندی سرور
```

### 🐛 عیب‌یابی

#### مشکلات رایج

**سرویس شروع نمی‌شود:**
```bash
# بررسی لاگ‌ها
journalctl -u hysteria-web -f

# بررسی وضعیت پورت
netstat -tulpn | grep :8080
```

**دسترسی از خارج امکان‌پذیر نیست:**
```bash
# بررسی فایروال
sudo ufw status
sudo ufw allow 8080/tcp
```

**کلاینت متصل نمی‌شود:**
```bash
# بررسی پیکربندی
cat /etc/hysteria/clientX.yaml

# تست اتصال
curl --socks5 localhost:SOCKS_PORT https://httpbin.org/ip
```

### 🤝 مشارکت

1. پروژه را Fork کنید
2. شاخه جدید بسازید (`git checkout -b feature/amazing-feature`)
3. تغییرات را Commit کنید (`git commit -m 'Add amazing feature'`)
4. شاخه را Push کنید (`git push origin feature/amazing-feature`)
5. Pull Request ایجاد کنید

### 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر فایل [LICENSE](LICENSE) را مطالعه کنید.

### 🙏 تشکر

- [Hysteria2](https://v2.hysteria.network/) برای پروتکل قدرتمند
- [Flask](https://flask.palletsprojects.com/) برای فریمورک وب
- جامعه متن‌باز برای ابزارهای فوق‌العاده

---

## English

### 📖 About

Hysteria2 Web Manager is a comprehensive and powerful management panel for Hysteria2 server and clients, built with Flask. This tool provides easy graphical management of Hysteria2 servers and clients.

### ✨ Key Features

#### 🖥️ Server Management
- ✅ **Automatic Installation** of Hysteria2 server
- ✅ **Easy Configuration** with GUI
- ✅ **Automatic SSL Certificate** generation
- ✅ **Systemd Service** management
- ✅ **Real-time Status** monitoring

#### 👥 Client Management
- ✅ **Add/Remove** clients
- ✅ **Automatic SOCKS5** configuration
- ✅ **Client Status** monitoring
- ✅ **Service Restart** functionality
- ✅ **Automatic Connection** testing

#### 📊 Monitoring & Logs
- ✅ **Real-time Logs** with filtering
- ✅ **System Information** (CPU, RAM, Network)
- ✅ **Interactive Status** charts
- ✅ **Automatic Alerts** on issues

#### 🎨 User Interface
- ✅ **Responsive Design** for mobile and desktop
- ✅ **Full Persian Support** (RTL)
- ✅ **Dark/Light Theme**
- ✅ **Beautiful Animations**

### 🛠️ Quick Installation

#### Method 1: Automatic Installation (Recommended)

```bash
# Download and run install script
curl -fsSL https://raw.githubusercontent.com/mohamadkazemt/hysteria2-web-manager/main/scripts/install.sh | sudo bash

# or
wget -O - https://raw.githubusercontent.com/mohamadkazemt/hysteria2-web-manager/main/scripts/install.sh | sudo bash
```

#### Method 2: Manual Installation

```bash
# Clone the project
git clone https://github.com/mohamadkazemt/hysteria2-web-manager.git
cd hysteria2-web-manager

# Run install script
sudo bash scripts/install.sh
```

### 🚀 Getting Started

After installation, start the service:

```bash
# Start service
hysteria-manager start

# Check status
hysteria-manager status

# View logs
hysteria-manager logs
```

Now visit:
```
http://YOUR_SERVER_IP:8080
```

### 📋 Management Commands

```bash
hysteria-manager start      # Start service
hysteria-manager stop       # Stop service
hysteria-manager restart    # Restart service
hysteria-manager status     # Service status
hysteria-manager logs       # Show logs
hysteria-manager enable     # Enable auto-start
hysteria-manager disable    # Disable auto-start
```

### 🛡️ Security Features

- 🔐 **Password Authentication**
- 🚫 **IP Restrictions** for access
- 📝 **Complete Logging** of all activities
- 🔒 **Encrypted Connections**

### 📚 API Documentation

#### System Status
```bash
GET /api/status
```

#### Client Management
```bash
GET /api/clients          # List clients
POST /api/clients         # Add client
DELETE /api/clients/{id}  # Remove client
```

#### Server Management
```bash
GET /api/server/status    # Server status
POST /api/server/install  # Install server
POST /api/server/setup    # Configure server
```

### 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit your Changes (`git commit -m 'Add amazing feature'`)
4. Push to the Branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [Hysteria2](https://v2.hysteria.network/) for the powerful protocol
- [Flask](https://flask.palletsprojects.com/) for the web framework
- Open source community for amazing tools

---

<div align="center">
Made with ❤️ for the Hysteria2 community
</div>
