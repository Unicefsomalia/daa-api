# Digtial Attendance Application - API 

## Introduction
Digital Attendance is an open-source project supported by UNICEF Somalia through a collaboration with [Sisitech](https://sisitech.com). The platform allows tracking of individual student attendance in schools.

It is comprised of three components:
- **API**: Django Rest Framework (this project)
- **Dashboard**: Angular Web Application 
- **Application**: Flutter Android Application 

## Digital Attendance Journey
- [Digital Attendance Journey Journey](https://drive.google.com/file/d/17T3VT-howD86XOSYrExLVMXWiXTiXimD/view)

## Docker Swarm Deployment Documentation
- [Deployment Docs](https://deploy.daasomalia.com/)

---

# Setup Guide

## Prerequisites

- Python 3.8 or higher
- Git
- A virtual environment tool like `venv` or `virtualenv`
- PostgreSQL (for database setup)

## Setup Instructions

### 1. Clone the Repository

Start by cloning the project repository from GitHub:

```bash
git clone https://github.com/Unicefsomalia/daa-api.git
cd daa-api
```

### 2. Create a Virtual Environment

Create and activate a virtual environment for the project using Python 3.8 or above:

```bash
# For Unix/Mac
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

With the virtual environment activated, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root of the project with the following content:

```env
SECRET_KEY="your_secret_key"
ALLOWED_HOSTS="localhost,api.domain.com"
DOCS_TITLE="Somalia"
DOCS_SUB_TITLE="API Docs"
DOCS_LOGO="https://path/to/logo.png"
DB_NAME="your_database_name"
DB_USER="your_database_user"
DB_PASSWORD="your_database_password"
DB_HOST="your_database_host"
DB_PORT=5432

EMAIL_HOST="smpt.domai.com"
EMAIL_HOST_USER=""
EMAIL_HOST_PASSWORD=""
SMTP_PORT=""
DEFAULT_FROM_EMAIL="Daa Somalia <somaliadaa@gmail.com>"

STATIC_ROOT=""
STATIC_URL=""

MEDIA_ROOT=""
MEDIA_URL=""
```

Replace the placeholder values (e.g., `your_secret_key`, `your_database_name`) with your actual configuration details.

### 5. Run Tests

To ensure everything is set up correctly, run the project's tests:

```bash
python manage.py test
```

If the tests pass successfully, your environment is ready!

### 6. Adding Reasons for Absence and Deletion in Django Admin

To add and manage the "reason for absence" and "reason for deletion" options, follow these steps in the Django admin panel:

1. **Access the Django Admin:**
   Log in to the Django admin panel. Ensure you have the necessary permissions to manage these options.

2. **Navigate to the Relevant Model:**
   In the Django admin dashboard, locate the models for managing "Reasons for Absence" and "Reasons for Deletion".

3. **Add or Edit Options:**
   For each of these models, add or edit the available reasons. Ensure that an option with name **"other"** is included. The **"other"** option will trigger the mobile application to present a text field for additional input.

   Setup in the admin panel:
   - **Reason for Absence Options:**
     - Sick
     - Family Emergency
     - Transportation Issues
     - other (Description: "Select this option to enter a custom reason")

   - **Reason for Deletion Options:**
     - Transferred
     - Graduated
     - Dropped Out
     - other (Description: "Select this option to enter a custom reason")

##  Want to Contribute or Have Any Questions?
We welcome contributions and feedback! If you want to contribute to this project or have any questions, reach out via email at hello@sisitech.com


