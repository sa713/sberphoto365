#!/bin/bash

set -e

# === НАСТРОЙКИ ===
PROJECT_DIR="/root/sberphoto365"
PYTHON_VERSION="python3"
SERVICE_NAME="sberphoto365"
BOT_FILE="bot.py"
LOG_FILE="$PROJECT_DIR/bot.log"
LOGROTATE_CONF="/etc/logrotate.d/${SERVICE_NAME}"

echo "🔧 Обновление системы и установка зависимостей..."
apt update
apt install -y $PYTHON_VERSION python3-pip curl logrotate

echo "📁 Переход в рабочую директорию..."
cd "$PROJECT_DIR"

echo "📦 Установка зависимостей глобально..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

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
ExecStart=/usr/bin/python3 $PROJECT_DIR/$BOT_FILE
Restart=always
RestartSec=5
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE
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
systemctl restart ${SERVICE_NAME}.service

echo "✅ Готово! Бот запущен как служба: systemctl status ${SERVICE_NAME}.service"
echo "📄 Лог доступен по пути: $LOG_FILE"
echo "ℹ️ Логи ротируются ежедневно, хранятся 7 архивов с компрессией."