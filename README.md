# Enrollment Management System (EMS)

A full-featured student enrollment management system built with **Python Flask**, **MySQL**, and **Bootstrap 5**.

---

## Features

- **Role-based access control** — Admin and Student roles
- **Admin**: Full CRUD on student records, search, dashboard stats
- **Student**: Self-registration, view and edit own profile
- **Authentication**: Secure login/logout with bcrypt password hashing
- **Flask-Login** session management
- **SQLAlchemy ORM** with 3NF database design
- **Bootstrap 5** responsive UI with custom CSS
- **Flash messages** for all user feedback
- **Form validation** (server-side via WTForms)

---

## Project Structure

```
project/
├── app.py               # Flask app, routes, CLI commands
├── models.py            # SQLAlchemy ORM models (User, Student)
├── forms.py             # WTForms form classes
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── templates/
│   ├── base.html        # Shared layout with sidebar
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html   # Admin & student dashboard
│   ├── students.html    # Admin: student list + search
│   ├── add_student.html # Admin: add student form
│   ├── edit_student.html# Admin: edit student form
│   ├── profile.html     # Student: view own profile
│   └── edit_profile.html# Student: edit own profile
└── static/
    └── style.css        # Custom styles
```

---

## Installation

### Prerequisites

- Python 3.9+
- MySQL Server 8.0+
- pip

### Step 1 — Clone / Download the project

```bash
cd your-project-folder
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Create the MySQL database

Open your MySQL client and run:

```sql
CREATE DATABASE enrollment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 5 — Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```
SECRET_KEY=change-this-to-a-random-string
DATABASE_URL=mysql+pymysql://YOUR_USER:YOUR_PASSWORD@localhost/enrollment_db
```

### Step 6 — Initialize the database and create admin

```bash
flask init-db
```

This creates all tables and seeds a default admin account:

| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `admin123` |

**Change the admin password after first login.**

### Step 7 — Run the app

```bash
flask run
```

Visit **http://127.0.0.1:5000** in your browser.

---

## Usage

### Admin

1. Log in with `admin` / `admin123`
2. Go to **Students** to view, search, add, edit, or delete students
3. Use **Add Student** to create student accounts directly

### Student

1. Go to **Register** to create a self-service account
2. Log in and view your profile on the **Dashboard**
3. Use **Edit Profile** to update your info or change your password

---

## Database Schema (3NF)

### `users` table

| Column        | Type         | Notes            |
|---------------|--------------|------------------|
| id            | INT (PK)     | Auto-increment   |
| username      | VARCHAR(80)  | Unique           |
| email         | VARCHAR(120) | Unique           |
| password_hash | VARCHAR(255) | bcrypt hash      |
| role          | ENUM         | admin / student  |

### `students` table

| Column         | Type         | Notes            |
|----------------|--------------|------------------|
| id             | INT (PK)     | Auto-increment   |
| user_id        | INT (FK)     | → users.id       |
| student_number | VARCHAR(20)  | Unique           |
| first_name     | VARCHAR(50)  |                  |
| last_name      | VARCHAR(50)  |                  |
| course         | VARCHAR(100) |                  |
| year_level     | INT          | 1–4              |
| contact_number | VARCHAR(20)  | Nullable         |

---

## Security Notes

- Passwords are hashed with **bcrypt** (never stored in plain text)
- CSRF protection on all forms via **Flask-WTF**
- Route-level protection via `@login_required` and `@admin_required`
- SQL injection prevention via **SQLAlchemy ORM**

---

## Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python 3, Flask 3       |
| ORM        | Flask-SQLAlchemy        |
| Auth       | Flask-Login, bcrypt     |
| Forms      | Flask-WTF, WTForms      |
| Database   | MySQL 8 + PyMySQL       |
| Frontend   | HTML5, Bootstrap 5.3    |
| Fonts      | Plus Jakarta Sans       |

---

## License

For academic use. Free to modify and extend.
