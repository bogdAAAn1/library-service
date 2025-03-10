# Django Signals

Django signals are used in conjunction with Celery to send Telegram notifications. After each new borrowing record is created, library administrators receive a notification about it.

---

# Celery

Celery is used to create and manage asynchronous tasks.

### Run Redis:

```
docker run -d -p 6379:6379 redis
```

### Celery Configuration

Add the following Celery configuration to your `.env` file:

```
CELERY_BROKER_URL=<CELERY_BROKER_URL>  
CELERY_RESULT_BACKEND=<CELERY_RESULT_BACKEND>  
CELERY_TIMEZONE=<CELERY_TIMEZONE>  
CELERY_TASK_TRACK_STARTED=<True/False>  
CELERY_TASK_TIME_LIMIT=<30 * 60>
```

### Running Celery

To start Celery, use the following command:

```
celery -A <project-name> worker --pool=solo --loglevel=info
```

---

# Django Celery Beat

Django Celery Beat is used to schedule periodic tasks. For example, it can be used to send notifications every day.

### Periodic Tasks

In this project, we have two scheduled tasks:

1. Sending notifications to a Telegram admin channel with general statistics on borrowings and overdue books.
2. Sending an email with detailed statistics of borrowings and overdue books, collected in an Excel file.

Both tasks run every morning.

### Installation

Add `django_celery_beat` to `INSTALLED_APPS` in `settings.py`:

```
INSTALLED_APPS = [
    # ... other apps
    "django_celery_beat",
]
```

Run migrations to set up the database tables for Celery Beat:

```
python manage.py migrate
```

### Running Django Celery Beat

To start Celery Beat, run the following command:

```
celery -A <project-name> beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

# Telegram Bot and Admin Channels

### Running the Telegram Bot

To start the Telegram bot, run:

```
python bot.py
```

### Bot Registration

First, register your bot using [@BotFather](https://t.me/BotFather) in Telegram. After obtaining your `TELEGRAM_BOT_TOKEN`, add it to your `.env` file:

```
TELEGRAM_BOT_TOKEN=<telegram_bot_token>
```

### Bot Functionality

#### 1. Admin Notifications

The bot automatically sends notifications to the admin channels. Administrators receive notifications about new borrowings, payments, and book returns. Morning summaries are also sent here.
Also, we have notifications via e-mail, every morning, or it can be changed on 
another suitable time.
To receive messages on corporate e-mail. You need just to change settings in .
env file.

To obtain the channel ID, make an API request:

```
https://api.telegram.org/<your_telegram_token>/sendMessage?chat_id=@<your_channel_name>&text=123
```

After obtaining the channel ID, add it to your `.env` file:

```
TELEGRAM_CHAT_ID=<telegram_chat_id>
```

Make sure you add your bot as an **Admin** in the channel.

#### 2. Customer Bot

Registered library users can use the Telegram bot to:

- View their current borrowings and borrowing history.
- Search for books by title and receive descriptions.
- Access a small FAQ section.

To search for a book, write in the bot chat.

```
@botname BookTitle
```