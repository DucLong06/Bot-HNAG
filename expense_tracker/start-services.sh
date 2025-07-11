#!/bin/bash

PROJECT_DIR="/home/longhd/project/tinhtienHNAG/Bot-HNAG/expense_tracker"  # Thay đổi path này
LOG_DIR="$PROJECT_DIR/logs"

# Tạo log directory
mkdir -p $LOG_DIR

echo "🚀 Starting Expense Tracker services..."

# Start Backend
cd $PROJECT_DIR/backend
source .venv/bin/activate
python manage.py migrate
nohup python manage.py runserver 0.0.0.0:8000 > $LOG_DIR/backend.log 2>&1 &
echo $! > $LOG_DIR/backend.pid
echo "✅ Backend started (PID: $(cat $LOG_DIR/backend.pid))"

# Start Frontend  
cd $PROJECT_DIR/frontend
nohup npm run dev > $LOG_DIR/frontend.log 2>&1 &
echo $! > $LOG_DIR/frontend.pid
echo "✅ Frontend started (PID: $(cat $LOG_DIR/frontend.pid))"

echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📊 Logs: $LOG_DIR/"