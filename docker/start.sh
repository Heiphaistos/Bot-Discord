#!/bin/sh

echo "[bot-discord] Starting web interface..."
python web_interface.py &
WEB_PID=$!

echo "[bot-discord] Starting Discord bot (auto-restart on failure)..."
while true; do
    python bot.py
    EXIT=$?
    echo "[bot-discord] bot.py exited with code $EXIT — restart in 10s..."
    # Si le web est mort aussi, on quitte tout
    kill -0 $WEB_PID 2>/dev/null || { echo "[bot-discord] Web interface down, exiting"; exit 1; }
    sleep 10
done &
BOT_LOOP_PID=$!

trap "kill $WEB_PID $BOT_LOOP_PID 2>/dev/null; exit 0" INT TERM

# Container reste vivant tant que le web interface tourne
wait $WEB_PID
