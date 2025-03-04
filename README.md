# **Django Project: MP Inscripción**

## **📌 Overview**
MP Inscripción is a Django-based web application designed for handling event registrations using dynamic forms. The application integrates `django-fobi` for form management, supports OAuth2 authentication for email sending via Gmail, and utilizes PostgreSQL as the database backend.

---

## **📂 Project Structure**
```
mp_inscripcion/      # Project root directory
│── inscripcion/     # Main application module
│── handler/         # Email and event handling module
│── templates/       # HTML templates for UI rendering
│── static/          # Static assets (CSS, JavaScript, Images)
│── mp/              # Django project settings and configurations
│── manage.py        # Django management script
```

---

## **🚀 Getting Started**
### **🔧 Prerequisites**
Ensure you have the following installed:
- Python 3.8+
- PostgreSQL 14+
- pip & virtualenv
- Google Cloud API credentials for OAuth2 authentication

### **📥 Installation**
1. **Clone the repository:**
   ```bash
   git clone https://github.com/movimientoperegrino/inscripcion
   cd inscripcion
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### **🛠 Configuration**
#### **Database Setup**
Modify the `DATABASES` settings in `mp/settings.py` to match your PostgreSQL configuration:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mp_inscripcion',
        'USER': 'mp',
        'PASSWORD': 'mp',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

#### **OAuth2 Email Configuration**
Set up OAuth2 credentials in `mp/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_OAUTH2_CLIENT_ID = 'your-client-id.apps.googleusercontent.com'
EMAIL_OAUTH2_CLIENT_SECRET = 'your-client-secret'
EMAIL_OAUTH2_REFRESH_TOKEN = 'your-refresh-token'
DEFAULT_CHARSET = "utf-8"
```
> ⚠️ **Do not hardcode credentials in `settings.py`. Use environment variables instead.**

#### **Run Database Migrations**
```bash
python manage.py migrate
```

#### **Create a Superuser**
```bash
python manage.py createsuperuser
```

---

## **🚀 Running the Project**
1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
2. Open `http://127.0.0.1:8000/` in your browser.

---
