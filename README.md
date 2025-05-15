# Electronic Voting System

A secure, transparent, and user-friendly platform for conducting electronic elections that I developed using Django.

![Electronic Voting System](static/images/evoting-preview.jpg)

## Overview

I created this Electronic Voting System as a Django-based web application designed to facilitate secure and transparent voting processes. It supports various election types, provides real-time results, and ensures the integrity of the democratic process through modern security measures.

## Features

### User Management
- User registration and authentication
- Profile management with personal information
- Activity tracking for audit purposes
- Role-based access control

### Elections
- Create and manage various types of elections
- Support for multiple candidates and positions
- Customizable voting periods
- Real-time vote counting and result visualization

### Security
- Encrypted ballots
- Verification mechanisms to prevent double voting
- Activity logging for audit trails
- Protection against common web vulnerabilities

### Content and Information
- Information pages about the voting process
- Blog with articles about elections and democracy
- FAQ section for common questions
- Contact form for inquiries

## Technologies Used

- **Backend**: Django 5.1.5, Python 3.12
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (recommended for production)
- **Security**: Django's built-in security features, encryption

## Installation

The project is available on my GitHub repository, and you can easily set it up by following these steps:

### Prerequisites
- Python 3.12+
- pip (Python package manager)
- Git

### Setup

1. Clone my repository:
   ```
   git clone https://github.com/michealamanya/evoting.git
   ```

2. Navigate to the project directory:
   ```
   cd voting_project
   ```

3. Create a virtual environment:
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Apply migrations:
   ```
   python manage.py migrate
   ```

7. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```
   python manage.py runserver
   ```

9. Access the application at http://127.0.0.1:8000/

## Project Structure

I've organized the codebase into several Django apps to maintain clean separation of concerns:

```
voting_project/
├── analytics/            # Analytics and statistics app
├── electronic_voting/    # Core voting functionality
├── notification/         # User notification system
├── pages/                # Static pages (about, FAQ, etc.)
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── user_management/      # User profile and authentication
└── voting_project/       # Project settings and configuration
```

## Usage

### For Administrators

1. Log in with your administrator credentials at `/admin/` 
{amanya as the name
 password "amanya@256"}
2. Create and manage elections
3. Monitor voting activity
4. View and export results

### For Voters

1. Register for an account
2. Log in to the system
3. Browse available elections
4. Cast your vote securely
5. View election results when published

## Security Considerations

In developing this application, I've implemented several security best practices:

- Secured the `SECRET_KEY` and kept it out of version control
- Configured for HTTPS in production environments
- Regular dependency updates
- Production settings with `DEBUG = False`
- Backup procedures for the database

## Troubleshooting

Based on my testing and user feedback, here are solutions to common issues:

- User profile errors: Check the signal handlers for profile creation
- Election display issues: Verify the election status dates
- Database errors: Run migrations to ensure schema is up to date

## License

I've released this project under the MIT License - see the LICENSE file for details.

## Contributors

While I (Micheal Amanya) am the primary developer of this project, I'd like to acknowledge:

- Several contributors from the open source community who provided feedback
- My colleagues who helped with testing and UX improvements

## Acknowledgments

I'm grateful to:
- The Django community for their excellent documentation
- Bootstrap team for their responsive design framework

## Contact

If you have questions or need support, feel free to reach out to me via GitHub or use the contact form on the site.
