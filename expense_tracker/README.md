# Expense Tracker

Expense Tracker is a full-stack application designed for shared expense management within groups. It streamlines the process of tracking costs, calculating debts, and settling payments using Telegram notifications and VietQR.

## Core Features
- **Shared Expenses**: Record costs and split them among group members.
- **Debt Summary**: Real-time view of balances and who owes whom.
- **Telegram Integration**: Automated notifications for new expenses and debt reminders.
- **VietQR Payments**: Generate QR codes for quick bank transfers.
- **Member Management**: Track bank account details and Telegram IDs for everyone in the group.

## Tech Stack
- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: Vue 3 (Composition API), TypeScript, Vuetify 3, Pinia
- **Infrastructure**: Docker, Docker Compose, Nginx, PostgreSQL

## Getting Started

### Prerequisites
- Docker and Docker Compose
- A Telegram Bot Token (from @BotFather)

### Setup
1. Clone the repository.
2. Create a `.env` file in the root directory based on `.env.example`:
   ```env
   DEBUG=0
   SECRET_KEY=your_django_secret_key
   TELEGRAM_BOT_TOKEN=your_bot_token
   POSTGRES_DB=expense_tracker
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_db_password
   ```
3. Build and start the services:
   ```bash
   docker-compose up --build -d
   ```
4. Run migrations and create a superuser:
   ```bash
   docker-compose exec backend python manage.py migrate
   # No need for superuser if using Telegram login, but good for admin
   docker-compose exec backend python manage.py createsuperuser
   ```

## Documentation
Detailed technical documentation can be found in the `/docs` directory:
- [Project Overview & PDR](docs/project-overview-pdr.md)
- [Codebase Summary](docs/codebase-summary.md)
- [Code Standards](docs/code-standards.md)
- [System Architecture](docs/system-architecture.md)

## License
MIT
