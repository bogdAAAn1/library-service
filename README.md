# Library Service API

## Table of content
1. [Project Description](#project-description)

2. [Features](#2-features)

3. [API Endpoints](#3-uapi-endpointsu)

   3.1 [Books Service](#31-books-service)

   3.2 [Users Service](#32-users-service)

   3.3 [Borrowings Service](#33-borrowings-service)

   3.4 [Payments Service (Stripe Integration)](#34-payments-service-stripe-integration)

   3.5 [Notifications Service (Telegram and Emails)](#35-notifications-service-telegram-and-emails)

     - [Admin Notifications](#351-admin-notifications)
     - [Customer Bot](#customer-bot)

4. [Getting Started](#4-getting-started)

   4.1 [Prerequisites](#41-prerequisites)

   4.2 [Installation from GitHub](#42-installation-from-github)

   4.3 [Running with Docker](#43-running-with-docker)

   4.4 [Running Background Services](#44-running-background-services)

5. [Testing](#5-testing)
6. [Documentation](#6-documentation)
7. [Contributing](#7-contributing)


## 1. Project Description

[Library Service API](./page_examples.md) is a web-based management system for a city library, 
enabling administrators to manage books, borrowings, users, and payments online. The system improves efficiency by replacing manual record-keeping with an automated API interface, providing features such as book inventory management, borrowing tracking, payment handling, and notifications.

## 2. Features

- **Books Management**: CRUD operations for books, including inventory tracking.

- **User Authentication**: JWT-based authentication and role-based access.

- **Borrowings Management**: users can borrow and return books while tracking 
  their due dates.

- **Filtering and pagination**: easy find items and view pages.

- **Payments Integration**: payments and fines handled through Stripe.

- **Notifications Service**: automatic notifications for borrowings, 
  overdue books, and payments via Telegram or email.

- **Admin Controls**: staff members can manage users and books, while regular 
  users can only borrow books.

- **Docker Support**: easy deployment using Docker and Docker Compose.



## 3. <u>API Endpoints</u>
### 3.1 Books Service

- `POST /books/` - Add a new book (Admin only)

- `GET /books/` - Get a list of books

- `GET /books/<id>/` - Get book details

- `PUT/PATCH /books/<id>/` - Update book details (Admin only)

- `DELETE /books/<id>/` - Delete a book (Admin only)

### 3.2 Users Service

- `POST /users/` - Register a new user

- `POST /users/token/` - Obtain JWT tokens

- `POST /users/token/refresh/` - Refresh JWT token

- `GET /users/me/` - Get current user profile

- `PUT/PATCH /users/me/` - Update user profile

### 3.3 Borrowings Service

- `POST /borrowings/` - Borrow a book

- `GET /borrowings/?user_id=...&is_active=...` - Get borrowings for user 

- `GET /borrowings/<id>/` - Get specific borrowing details

- `POST /borrowings/<id>/return/` - Return a book

### 3.4 Payments Service (Stripe Integration)

- `GET /success/` - Confirm successful payment

- `GET /cancel/` - Payment cancelled

### 3.5 Notifications Service (Telegram and Emails)

- Automatic notifications for:

    - New borrowings

    - Overdue borrowings

    - Successful payments

#### Admin Notifications

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

#### Customer Bot

Registered library users can use the Telegram bot to:

- View their current borrowings and borrowing history.
- Search for books by title and receive descriptions.
- Access a small FAQ section.

To search for a book, write in the bot chat.

```
@botname BookTitle
```

More detailed information about setting-up notifications [**here.**](telegram_bot.md)

# 4. Getting Started

## 4.1 Prerequisites

- Python 3.9+

- Docker & Docker Compose

- PostgreSQL

- Redis

- Stripe API keys

- Telegram Bot API token

## 4.2 Installation from GitHub

You can find instructions here: [instructions](./github_installation.md) 

## 4.3 Running with Docker

1. Build and start the services:

        docker-compose up --build

2. Access the API at `http://127.0.0.1:8000/api/`

## 4.4 Running Background Services

- Start the Celery worker (if used):

        celery -A library_service worker --loglevel=info

- Start the Telegram bot notification service:

      python manage.py start_notifications

## 5. Testing

Run unit tests:

    pytest

## 6. Documentation

- **Swagger UI** is available at `http://127.0.0.1:8000/api/doc/swagger/`

- **ReDoc** is available at `http://127.0.0.1:8000/api/doc/redoc/`

## 7. Contributing

1. Fork the repository.

2. Create a feature branch (`git checkout -b feature-name`).

3. Commit changes (`git commit -m 'Add new feature')`.

4. Push to the branch (`git push origin feature-name`).

5. Open a pull request.