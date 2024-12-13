# Lunch Bot HNAG

Bot Telegram hỗ trợ vote món ăn và chia tiền cho nhóm.

## Tính năng

- 🗳️ Tạo poll chọn món ăn tự động
- 💰 Tính tiền và chia đều cho nhóm
- 📋 Quản lý danh sách món ăn
- 🕒 Tự động chạy theo lịch

## Cài đặt

1. Clone repository:
```bash
git clone git@github.com:DucLong06/Bot-HNAG.git
cd Bot-HNAG
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Cấu hình bot:
   - Tạo file `config.py` với nội dung:
```python
# Bot settings
TOKEN = "your_telegram_bot_token"
CHAT_ID = "your_telegram_group_chat_id"

# File paths
FOOD_FILE = "data/foods.json"
ACTIVE_VOTE_FILE = "data/active_votes.json"
COMPLETED_VOTE_FILE = "data/completed_votes.json"

# Default food list
DEFAULT_FOOD_LIST = {
    "foods": [
        "Bún bò Huế",
        "Bún chả",
        "Cơm gà",
        "Bún đậu mắm tôm",
        # Thêm các món khác...
    ]
}
```

## Chạy Bot

### Chạy thủ công
```bash
# Chạy bot
python main.py --run

# Tạo vote
python main.py --vote

# Đóng vote
python main.py --close-vote
```

### Chạy tự động với Crontab

1. Mở crontab:
```bash
crontab -e
```

2. Thêm các lệnh:
```bash
# Khởi động bot khi reboot
@reboot cd /path/to/your/bot && python3 run_bot.py --run

# Tạo vote 10:45 các ngày thứ 2-6
45 10 * * 1-5 cd /path/to/your/bot && python3 main.py --vote

# Đóng vote 12:10 các ngày thứ 2-6
10 12 * * 1-5 cd /path/to/your/bot && python3 main.py --close-vote
```

## Lệnh Bot

### Quản lý món ăn
- `/add [tên món]` - Thêm món ăn mới
- `/list` - Xem danh sách món ăn
- `/remove [tên món]` - Xóa món ăn

### Tính tiền
- `/debt [số tiền]` - Khai báo số tiền (dành cho người được chọn trả tiền)
- `/pay [@user1 @user2]` - Thêm người vào danh sách chia tiền

## Luồng hoạt động

1. **10:45** - Bot tự động tạo poll chọn món
2. **12:10** - Bot đóng poll và công bố kết quả
3. Người trả tiền dùng lệnh `/debt [số tiền]`
4. Bot tính và hiển thị số tiền mỗi người cần trả
5. Nếu có người quên vote, dùng `/pay` để thêm vào

## Xử lý lỗi

### Kiểm tra log
```bash
# Xem log của bot
tail -f bot.log

# Xem log của cron
tail -f /var/log/syslog | grep CRON
```

### Khởi động lại bot
```bash
# Dừng bot
python run_bot.py --stop

# Chạy lại
python run_bot.py --run
```

## Cấu trúc dự án
```
lunch-bot/
├── main.py           # Entry point
├── run_bot.py        # Bot runner
├── config.py         # Configuration
├── utils.py          # Utility functions
├── data/            
│   ├── foods.json    # Food list
│   ├── active_votes.json
│   └── completed_votes.json
├── requirements.txt  # Dependencies
└── README.md
```

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## License

[MIT License](LICENSE)