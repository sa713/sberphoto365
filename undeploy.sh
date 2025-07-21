# v1.0
#!/bin/bash

set -e

# === НАСТРОЙКИ ===
PROJECT_DIR="/root/sberphoto365"
SERVICE_NAME="sberphoto365"
LOG_FILE="$PROJECT_DIR/bot.log"
LOGROTATE_CONF="/etc/logrotate.d/${SERVICE_NAME}"

echo "🛑 Остановка systemd-сервиса..."
systemctl stop ${SERVICE_NAME}.service || echo "Сервис не запущен"

echo "❌ Отключение автозапуска..."
systemctl disable ${SERVICE_NAME}.service || true

echo "🗑 Удаление systemd unit-файла..."
rm -f /etc/systemd/system/${SERVICE_NAME}.service

echo "🔄 Перезапуск systemd daemon..."
systemctl daemon-reexec
systemctl daemon-reload

echo "🗑 Удаление логов и logrotate-конфига..."
rm -f "$LOG_FILE"
rm -f "$LOGROTATE_CONF"

echo "✅ Служба и логи удалены."

read -p "❓ Удалить сам проект в $PROJECT_DIR? (y/N): " confirm
if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    rm -rf "$PROJECT_DIR"
    echo "📁 Проект удалён."
else
    echo "📁 Проект сохранён."
fi

echo "✅ Всё готово."
