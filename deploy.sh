#!/bin/bash

set -e

# === НАСТРОЙКИ ===
PROJECT_DIR="/root/sberphoto365"
PYTHON_VERSION="python3"
SERVICE_NAME="sberphoto365"
VENV_DIR="$PROJECT_DIR/venv"
BOT_FILE="bot.py"

echo "🔧 Обновление системы и установка зависимостей..."
apt update
apt install -y $PYTHON_VERSION python3-pip python3-venv

echo "📁 Создание рабочей директории..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "🐍 Создание виртуального окружения..."
$PYTHON_VERSION -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🛠 Инициализация базы данных..."
$PYTHON_VERSION init_db.py

echo "📝 Создание systemd unit-файла..."
cat > /etc/systemd/system/${SERVICE_NAME}.service <<EOF
[Unit]
Description=Telegram Photo Challenge Bot (365)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python3 $PROJECT_DIR/$BOT_FILE
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

echo "📄 Создание конфигурации logrotate..."
cat > "$LOGROTATE_CONF" <<EOF
$LOG_FILE {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

echo "🔄 Перезапуск systemd и запуск бота как службы..."
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}.service
systemctl start ${SERVICE_NAME}.service

echo "✅ Готово! Бот запущен как служба: systemctl status ${SERVICE_NAME}.service"
echo "ℹ️ Логи ротируются ежедневно, сохраняются 7 архивных копий с сжатием."
