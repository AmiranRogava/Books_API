# Flask RESTful API Project

This is a Flask RESTful API project for managing books and users.

## Setup

1. **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Database setup:**
    - This project uses SQLite. The database file will be created as `books.db`.
    - Ensure you have SQLite installed. If not, install it according to your OS instructions.

4. **Run the application:**
    ```bash
    python app.py
    ```

## API Endpoints

### Authentication
# NOTE: ! you should remove @admin_check in order to create super admin and then put it back to use that admin
- **POST /auth**: Register a new user (Admin only).
    - Requires username, password, and role in the request body.
    - Only admin users can register new users.

- **GET /auth**: User login.
    - Requires username and password in the request body.

### Books

- **GET /books**: Get a list of all books.
    - No authentication required.

- **POST /books**: Add a new book.
    - Requires title and author in the request body.
    - User authentication required.

- **GET /books/<book_id>**: Get details of a specific book by ID.
    - No authentication required.

- **PUT /books/<book_id>**: Update details of a specific book by ID.
    - Requires title and/or author in the request body.
    - User authentication required.

- **DELETE /books/<book_id>**: Delete a specific book by ID.
    - User authentication required.

## Authentication

- Admin users can perform user registration and manage books.
- Regular users can only manage books.

## Authorization

- Users need to authenticate to access most endpoints.
- Admin access is required for user registration.
