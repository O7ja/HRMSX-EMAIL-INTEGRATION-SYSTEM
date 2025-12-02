# PythonAnywhere Deployment Instructions for HRMSX EMAIL INTEGRATION SYSTEM

## Step 1: Create Account & Upload Files
1. Go to pythonanywhere.com and create an account
2. Upload your project files via Git or through the web interface

## Step 2: Set Up Virtual Environment
```bash
# SSH into PythonAnywhere
cd /home/yourusername
git clone https://github.com/O7ja/HRMSX-EMAIL-INTEGRATION-SYSTEM.git
cd HRMSX-EMAIL-INTEGRATION-SYSTEM
mkvirtualenv --python=/usr/bin/python3.10 hrmsx_env
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables
Create `.env` file in project root:
```
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com,127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Step 4: Update Django Settings
Update settings.py for production:
- Change DEBUG = False
- Update ALLOWED_HOSTS with your domain
- Configure static files

## Step 5: Create WSGI Configuration
In PythonAnywhere Web tab:
- Add a new web app
- Choose Manual Configuration → Python 3.10
- Set WSGI configuration file path

## Step 6: Database Migration
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## Step 7: Configure Celery (Optional for background tasks)
PythonAnywhere doesn't support Celery directly on free tier.
For paid accounts, use:
```bash
celery -A email_integration_system worker -l info
celery -A email_integration_system beat -l info
```

## Step 8: Reload Web App
Click "Reload" in PythonAnywhere Web tab

## Important Notes:
- Change SECRET_KEY before deployment
- Never commit .env file (already in .gitignore)
- Celery requires paid account or alternative task queue
- Keep DEBUG=False in production
- Use environment variables for sensitive data
