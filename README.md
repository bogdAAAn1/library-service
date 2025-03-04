# Library Service API

## Project Description

[Library Service API](./page_examples.md) is a web-based management system for a city library, 
enabling administrators to manage books, borrowings, users, and payments online. The system improves efficiency by replacing manual record-keeping with an automated API interface, providing features such as book inventory management, borrowing tracking, payment handling, and notifications.

## Features

- **Books Management**: CRUD operations for books, including inventory tracking.

- **User Authentication**: JWT-based authentication and role-based access.

- **Borrowings Management**: Users can borrow and return books while tracking 
  their due dates.

- **Filtering and pagination**: Easy find items and view pages.

- **Payments Integration**: Payments and fines handled through Stripe.

- **Notifications Service**: Automatic notifications for borrowings, overdue 
  books, and payments via Telegram.

- **Admin Controls**: Staff members can manage users and books, while regular 
  users can only borrow books.

- **Docker Support**: Easy deployment using Docker and Docker Compose.



## <u>API Endpoints</u>
### Books Service

- `POST /books/` - Add a new book (Admin only)

- `GET /books/` - Get a list of books

- `GET /books/<id>/` - Get book details

- `PUT/PATCH /books/<id>/` - Update book details (Admin only)

- `DELETE /books/<id>/` - Delete a book (Admin only)

### Users Service

- `POST /users/` - Register a new user

- `POST /users/token/` - Obtain JWT tokens

- `POST /users/token/refresh/` - Refresh JWT token

- `GET /users/me/` - Get current user profile

- `PUT/PATCH /users/me/` - Update user profile

### Borrowings Service

- `POST /borrowings/` - Borrow a book

- `GET /borrowings/?user_id=...&is_active=...` - Get borrowings for user 

- `GET /borrowings/<id>/` - Get specific borrowing details

- `POST /borrowings/<id>/return/` - Return a book

### Notifications Service

- Automatic notifications for:

    - New borrowings

    - Overdue borrowings

    - Successful payments

### Payments Service (Stripe Integration)

- `GET /success/` - Confirm successful payment

- `GET /cancel/` - Payment cancelled

# Getting Started

## Prerequisites

- Python 3.9+

- Docker & Docker Compose

- PostgreSQL

- Redis

- Stripe API keys

- Telegram Bot API token

## Installation from GitHub

You can find instructions here: [instructions](./github_installation.md) 

## Running with Docker

1. Build and start the services:

        docker-compose up --build

2. Access the API at `http://127.0.0.1:8000/api/`

## Running Background Services

- Start the Celery worker (if used):

        celery -A library_service worker --loglevel=info

- Start the Telegram bot notification service:

      python manage.py start_notifications

## Testing

Run unit tests:

    pytest

## Documentation

- **Swagger UI** is available at `http://127.0.0.1:8000/api/doc/swagger/`

- **ReDoc** is available at `http://127.0.0.1:8000/api/doc/redoc/`

## Contributing

1. Fork the repository.

2. Create a feature branch (`git checkout -b feature-name`).

3. Commit changes (`git commit -m 'Add new feature')`.

4. Push to the branch (`git push origin feature-name`).

5. Open a pull request.

