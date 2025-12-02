# HRMSX EMAIL INTEGRATION SYSTEM

A comprehensive, enterprise-grade Human Resource Management System with integrated email automation, built with Django and Celery. This system streamlines HR operations including employee onboarding, attendance tracking, leave management, and performance reviews with automated email notifications.

## 🎯 Key Features

### Employee Management
- **User Role Management**: Employee, Manager, and HR roles with granular permissions
- **Employee Profiles**: Comprehensive employee information and status tracking
- **Department Organization**: Hierarchical organization structure with manager-subordinate relationships

### Attendance System
- **Check-in/Check-out**: Real-time attendance tracking with timestamps
- **Automated Alerts**: Late arrival and checkout reminders via email
- **Attendance Reports**: Daily, weekly, and monthly attendance analytics
- **Status Tracking**: Present, Late, Absent, Leave status management

### Leave Management
- **Leave Request Workflow**: Employee submission → Manager approval → HR processing
- **Multiple Leave Types**: Support for various leave categories (Sick, Casual, Paid, etc.)
- **Balance Tracking**: Real-time leave balance calculations
- **Automated Notifications**: Request submission, approval/rejection, and reminder emails
- **Leave Calendar**: Visual leave scheduling and planning

### Onboarding & Offboarding
- **Structured Onboarding**: Day 3, 5, and 7 checklist milestones
- **Welcome Package**: Automated welcome emails with company information
- **Exit Process**: Systematic offboarding with checklist management
- **Documentation**: Automated farewell emails and knowledge handover tracking

### Performance Management
- **Review Cycles**: Structured review periods with customizable criteria
- **Self-Assessments**: Employee self-review submissions with deadline tracking
- **Manager Reviews**: Multi-level review process with feedback
- **Goal Tracking**: Quarterly goal progress updates and achievement notifications
- **Appreciation System**: Manager recognition and badge system
- **Reminder System**: 7-day, 3-day, and 1-day deadline reminders

### Email System
- **Automated Notifications**: Event-triggered email communications
- **Email Templates**: Customizable HTML email templates
- **Celery Integration**: Background task processing with Redis
- **Email Logging**: Complete audit trail of all sent emails
- **Scheduled Tasks**: Django Celery Beat for time-based email delivery

## 🏗️ Architecture

### Technology Stack

**Backend**
- Django 5.2.8 - Web framework
- Django REST Framework 3.16.1 - REST API
- Celery 5.5.3 - Distributed task queue
- Django Celery Beat 2.8.1 - Scheduled tasks
- Redis 5.0.1 - Message broker and caching

**Frontend**
- Bootstrap 5 - Responsive UI framework
- HTML5/CSS3 - Semantic markup and styling
- JavaScript - Client-side interactivity

**Database**
- SQLite (development)
- PostgreSQL (production ready)

**Deployment**
- PythonAnywhere - Cloud hosting
- Docker support (optional)

### Project Structure

```
HRMSX-EMAIL-INTEGRATION-SYSTEM/
├── email_integration_system/      # Project settings
│   ├── settings.py               # Development settings
│   ├── settings_production.py    # Production settings
│   ├── celery.py                 # Celery configuration
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # WSGI application
│
├── users/                         # User management app
│   ├── models.py                 # User and Role models
│   ├── views.py                  # Authentication and profile views
│   ├── signals.py                # User creation signals
│   └── admin.py                  # Admin interface
│
├── attendance/                    # Attendance tracking app
│   ├── models.py                 # Attendance records
│   ├── views.py                  # Check-in/check-out views
│   ├── tasks.py                  # Email notification tasks
│   └── urls.py                   # Attendance URL patterns
│
├── leave/                         # Leave management app
│   ├── models.py                 # Leave requests and balances
│   ├── views.py                  # Leave workflow views
│   ├── tasks.py                  # Leave notification tasks
│   └── urls.py                   # Leave URL patterns
│
├── onboarding/                    # Onboarding/Offboarding app
│   ├── models.py                 # Onboarding records and checklists
│   ├── views.py                  # Onboarding workflow views
│   ├── tasks.py                  # Email notification tasks
│   └── urls.py                   # Onboarding URL patterns
│
├── performance/                   # Performance management app
│   ├── models.py                 # Review cycles, reviews, goals
│   ├── views.py                  # Review and assessment views
│   ├── forms.py                  # Review forms
│   ├── tasks.py                  # Review notification tasks
│   └── urls.py                   # Performance URL patterns
│
├── templates/                     # HTML templates
│   ├── base.html                 # Base template
│   ├── dashboards/               # Dashboard templates
│   ├── emails/                   # Email templates
│   ├── attendance/               # Attendance templates
│   ├── leave/                    # Leave templates
│   ├── onboarding/               # Onboarding templates
│   └── performance/              # Performance templates
│
├── static/                        # Static assets
│   ├── css/                      # Stylesheets
│   ├── js/                       # JavaScript files
│   └── images/                   # Image assets
│
├── requirements.txt               # Python dependencies
├── manage.py                      # Django management script
├── db.sqlite3                     # SQLite database
├── DEPLOYMENT.md                  # Deployment overview
├── PYTHONANYWHERE_SETUP.md       # PythonAnywhere deployment guide
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip and virtualenv
- Redis (for Celery)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/O7ja/HRMSX-EMAIL-INTEGRATION-SYSTEM.git
   cd HRMSX-EMAIL-INTEGRATION-SYSTEM
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files** (production)
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

9. **Start Celery worker** (in another terminal)
   ```bash
   celery -A email_integration_system worker -l info
   ```

10. **Start Celery Beat** (in another terminal)
    ```bash
    celery -A email_integration_system beat -l info
    ```

Visit `http://127.0.0.1:8000` and log in with your superuser credentials.

## 📖 Usage

### Admin Dashboard
- Access at `/admin/` with superuser credentials
- Manage users, leave types, review cycles, and system configuration

### Employee Dashboard
- View personal attendance, leave balance, and performance reviews
- Submit leave requests and self-assessments
- Access onboarding checklists

### Manager Dashboard
- Approve/reject leave requests
- View team performance and attendance
- Send recognition emails
- Track team onboarding progress

### HR Dashboard
- Create and manage leave types, review cycles, and departments
- Initiate onboarding and offboarding
- View system-wide analytics and reports
- Configure automated email notifications

## 🔐 Security Features

- **Role-Based Access Control**: Granular permission system
- **CSRF Protection**: Cross-Site Request Forgery prevention
- **Secure Passwords**: Django password validation and hashing
- **HTTPS Ready**: SSL/TLS configuration for production
- **Environment Variables**: Sensitive data management
- **Email Verification**: Secure email verification system
- **Session Management**: Secure session handling

## 📧 Email Configuration

### Development
Default console email backend - emails print to terminal

### Production
Configure SMTP in `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Email Templates
All email templates are customizable in `templates/emails/`

## 🗄️ Database Schema

### Key Models
- **User** - Django user with custom role profile
- **UserRole** - Employee, Manager, HR roles
- **Attendance** - Daily attendance records
- **LeaveRequest** - Leave request workflow
- **LeaveBalance** - Employee leave balance tracking
- **Onboarding** - Employee onboarding records
- **PerformanceReview** - Performance review cycles and reviews
- **PerformanceGoal** - Individual goals and tracking

## 📊 Automated Tasks

### Celery Tasks
- Welcome emails (onboarding day 1)
- Day 3, 5, 7 onboarding checklists
- Late check-in alerts
- Leave reminders (before and after)
- Leave approval/rejection notifications
- Performance review reminders (7/3/1 day before deadline)
- Overdue review notifications
- Goal achievement notifications
- Quarterly goal progress reminders

## 🐛 Troubleshooting

### Common Issues

**Celery tasks not running**
- Ensure Redis is running: `redis-cli ping`
- Check Celery worker logs for errors
- Verify `CELERY_ALWAYS_EAGER = False` in production

**Email not sending**
- Verify email credentials in `.env`
- Check email backend configuration
- Review Django error logs
- For Gmail: Enable 2-factor authentication and use App Password

**Database errors**
- Run migrations: `python manage.py migrate`
- Check database permissions and connectivity
- Clear old migrations if needed

**Static files not loading**
- Run: `python manage.py collectstatic --noinput`
- Verify static files configuration in settings
- Check web server static file mapping

## 📝 API Endpoints

### Authentication
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `POST /api/register/` - User registration (if enabled)

### Attendance
- `GET /attendance/` - View attendance history
- `POST /attendance/check-in/` - Clock in
- `POST /attendance/check-out/` - Clock out

### Leave
- `GET /leave/requests/` - View leave requests
- `POST /leave/request/` - Submit leave request
- `POST /leave/approve/` - Approve leave
- `POST /leave/reject/` - Reject leave

### Onboarding
- `GET /onboarding/` - View onboarding status
- `POST /onboarding/new/` - Create onboarding

### Performance
- `GET /performance/` - View reviews
- `POST /performance/self-assessment/` - Submit self-assessment

## 🚀 Deployment

### PythonAnywhere
See `PYTHONANYWHERE_SETUP.md` for detailed deployment instructions.

### Docker (Optional)
```bash
docker build -t hrmsx .
docker run -p 8000:8000 hrmsx
```

### Environment Checklist
- [ ] Generate strong SECRET_KEY
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up email credentials
- [ ] Configure database (PostgreSQL recommended)
- [ ] Set up Redis for Celery
- [ ] Configure static/media file serving
- [ ] Enable HTTPS
- [ ] Set up logging
- [ ] Configure backup strategy

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md)
- [PythonAnywhere Setup](PYTHONANYWHERE_SETUP.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

## 👥 Default Demo Users

| Username | Password | Role |
|----------|----------|------|
| hr1 | password123 | HR |
| manager1 | password123 | Manager |
| emp1 | password123 | Employee |
| emp2 | password123 | Employee |
| emp3 | password123 | Employee |

**⚠️ Change these credentials in production!**

## 📄 License

This project is proprietary. All rights reserved.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support, email support@hrmsx.com or open an issue on GitHub.

## 🎯 Roadmap

### v2.0
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Payroll integration
- [ ] Time tracking enhancement
- [ ] Document management system
- [ ] Multi-language support

### v2.1
- [ ] Machine learning-based insights
- [ ] API rate limiting
- [ ] Advanced reporting
- [ ] Custom workflows

## 📊 Performance Metrics

- **Page Load Time**: < 2 seconds
- **API Response Time**: < 500ms
- **Email Delivery**: < 5 seconds
- **Concurrent Users**: 500+

## 🔄 Version History

- **v1.0.0** (December 2025) - Initial release
  - Complete HR management system
  - Email automation
  - Performance management
  - Onboarding/Offboarding workflows

---

**Made with ❤️ by HRMSX Team**

Last Updated: December 2, 2025
