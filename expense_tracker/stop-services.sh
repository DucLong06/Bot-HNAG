#!/bin/bash

PROJECT_DIR="/home/longhd/project/tinhtienHNAG/Bot-HNAG/expense_tracker" 
LOG_DIR="$PROJECT_DIR/logs"

echo "🛑 Stopping Expense Tracker services..."

# Stop Backend
if [ -f $LOG_DIR/backend.pid ]; then
    kill $(cat $LOG_DIR/backend.pid) 2>/dev/null
    rm $LOG_DIR/backend.pid
    echo "✅ Backend stopped"
else
    echo "⚠️ Backend PID file not found"
fi

# Stop Frontend
if [ -f $LOG_DIR/frontend.pid ]; then
    kill $(cat $LOG_DIR/frontend.pid) 2>/dev/null
    rm $LOG_DIR/frontend.pid
    echo "✅ Frontend stopped"
else
    echo "⚠️ Frontend PID file not found"
fi

# Kill any remaining processes
pkill -f "manage.py runserver"
pkill -f "npm run dev"
pkill -f "npm run dev"


pkill -f "manage.py runserver"
pkill -f "python manage.py"

pkill -f "node"
echo "🏁 All services stopped"