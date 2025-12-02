# PythonAnywhere Deployment Checklist

## Pre-Deployment Steps (on your local machine)

- [ ] Generate a new SECRET_KEY
  ```python
  from django.core.management.utils import get_random_secret_key
  print(get_random_secret_key())
  ```

- [ ] Update .env file with production values
- [ ] Test locally: `python manage.py runserver`
- [ ] Run migrations locally: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Create superuser (if needed): `python manage.py createsuperuser`
- [ ] Commit and push to GitHub

## PythonAnywhere Setup Steps

### 1. Create Account & Setup
```bash
# Log in to PythonAnywhere at https://www.pythonanywhere.com
# Go to "Consoles" → "New console" → "Bash"

# Clone your repository
cd /home/yourusername
git clone https://github.com/O7ja/HRMSX-EMAIL-INTEGRATION-SYSTEM.git
cd HRMSX-EMAIL-INTEGRATION-SYSTEM
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 hrmsx_env

# Activate it (should be automatic after mkvirtualenv)
workon hrmsx_env

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Create .env file in project root
nano .env
```

Paste the following (update values):
```
SECRET_KEY=generate-new-one-and-paste-here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com,127.0.0.1,localhost
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### 4. Setup Database
```bash
# Run migrations
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser
# Follow prompts to create admin user

# Collect static files
python manage.py collectstatic --noinput
```

### 5. Configure Web App in PythonAnywhere
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration" → "Python 3.10"
4. In the WSGI configuration file, add this code:

```python
import os
import sys
from pathlib import Path

project_dir = '/home/yourusername/HRMSX-EMAIL-INTEGRATION-SYSTEM'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'email_integration_system.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. Set Virtualenv: `/home/yourusername/.virtualenvs/hrmsx_env`

6. Configure Source code directory: `/home/yourusername/HRMSX-EMAIL-INTEGRATION-SYSTEM`

7. Configure Static files:
   - URL: `/static/`
   - Directory: `/home/yourusername/HRMSX-EMAIL-INTEGRATION-SYSTEM/staticfiles/`

### 6. Final Configuration

#### Static Files (in PythonAnywhere Web tab)
- Click "Add a new static files mapping"
- URL: `/static/`
- Directory: `/home/yourusername/HRMSX-EMAIL-INTEGRATION-SYSTEM/staticfiles/`

#### Static Files (in PythonAnywhere Web tab)
- Click "Add a new static files mapping"
- URL: `/media/`
- Directory: `/home/yourusername/HRMSX-EMAIL-INTEGRATION-SYSTEM/media/`

### 7. Reload & Test
1. Click "Reload" button in Web tab
2. Visit your domain: `https://yourusername.pythonanywhere.com`
3. Log in with admin credentials at `/admin/`

## Post-Deployment

### Set Up Email (Gmail)
1. Enable 2-factor authentication on Gmail
2. Create App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character password in .env as EMAIL_HOST_PASSWORD

### Optional: Setup Celery Beat
If on paid account, in Bash console:
```bash
celery -A email_integration_system beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Monitor Logs
In PythonAnywhere Web tab, scroll down to "Log files" section to view:
- Error log
- Server log

### Troubleshooting
- Check error logs first
- Ensure .env file has correct permissions
- Verify SECRET_KEY is strong
- Check email credentials are correct
- Ensure database migrations are applied

## Security Checklist
- [ ] SECRET_KEY is strong and not default
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Email credentials stored in .env (not in code)
- [ ] HTTPS is enabled (default on PythonAnywhere)
- [ ] CSRF protection enabled
- [ ] Session cookies are secure
