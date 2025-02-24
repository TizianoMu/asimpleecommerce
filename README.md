# asimpleecommerce

## Overview

**asimpleecommerce** is a backoffice application for managing an e-commerce platform. It allows administrators to handle customers, products, and categories through a web-based interface. The application is built using **Flask** for the backend and leverages **Axios**, **Bootstrap**, and **Font Awesome** for the frontend.

## Features

- **User Authentication**: Login and registration system with JWT-based authentication.
- **Common Management**: Add, update, and delete resources.
- **Dynamic Modals**: Use Bootstrap modals to handle form submissions dynamically.
- **Session Handling**: Cookie-based authentication using JWT tokens.
- **KPI page**: A page for showing charts of sales data.

## Project Structure

```
asimpleecommerce/
│   .env
│   docker-compose.yaml
│   README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── run.py
│   ├── app/
│   │   ├── config.py
│   │   ├── jwt_handlers.py
│   │   ├── models.py
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── routes.py
│   │   │   ├── __init__.py
│   │   │   ├── admin/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── schemas.py
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   ├── base.css
│   │   │   ├── js/
│   │   │   │   ├── auth.js
│   │   │   │   ├── dynamic_modal.js
│   │   │   │   ├── form_manager.js
│   │   ├── templates/
│   │   │   ├── admin/
│   │   │   │   ├── common_admin.html
│   │   │   │   ├── analytics.html
│   │   │   ├── auth/
│   │   │   │   ├── login.html
│   │   │   │   ├── register.py
│   │   │   ├── base.html
│   │   │   ├── home.html
│   │   │   ├── dynamic_modal.html
│   │   │   ├── navbar.html
│   ├── migrations/
```

## Technologies Used

- **Backend**: Flask, SQLAlchemy, JWT
- **Frontend**: Bootstrap, Font Awesome
- **JavaScript**: Axios, Vanilla JS
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose

## Installation

### Prerequisites

- Docker & Docker Compose installed on your system.

### Steps

1. Clone the repository:
   ```sh
   git clone https://github.com/TizianoMu/asimpleecommerce.git
   cd asimpleecommerce
   ```
2. Create a `.env` file in the project root and configure environment variables.
3. Build and start the application:
   ```sh
   docker-compose up --build
   ```
4. Access the application at `http://localhost:5000`.

## Authentication & API Calls

- The **auth.js** file handles form submission dynamically by intercepting forms with the `data-url` attribute and sending requests via Axios.
- The **dynamic\_modal.js** file is responsible for opening Bootstrap modals dynamically based on the form being used.

## Database Migrations

To apply database migrations, use the following commands inside the backend container:

```sh
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributors

- Tiziano Murzio ([tiziano.murzio@outlook.it](mailto\:tiziano.murzio@outlook.it))

