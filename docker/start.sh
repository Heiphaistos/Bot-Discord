#!/bin/sh
set -e

echo "[bot-discord] Starting web interface..."
python web_interface.py &
WEB_PID=$!

echo "[bot-discord] Starting Discord bot..."
python bot.py &
BOT_PID=$!

trap "kill $WEB_PID $BOT_PID 2>/dev/null; exit 0" INT TERM

wait $BOT_PID
kill $WEB_PID 2>/dev/null
