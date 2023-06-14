# Online Event Registration System

The Online Event Registration System is a web application built using Django REST Framework. It provides an API-based system for event organizers to create and manage events, while participants can register and sign up for these events. The system aims to simplify event management tasks, enhance communication between organizers and participants, and provide a seamless registration experience.

## Features

- User Registration and Authentication
- Event Creation and Management
- Event Registration
- Search and Filtering
- Event Notifications
- User Dashboard
- Admin Panel

## Tech Stack

- Django REST Framework
- PostgreSQL or MySQL (Database)
- Django's Token-based Authentication
- Django's Email Sending Capabilities

## Getting Started

### Prerequisites

- Python (version 3.7 or higher)
- Django (version 3.2 or higher)
- Django REST Framework (version 3.12 or higher)
- PostgreSQL or MySQL (database server)

### Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/mjavadf/evently
   ```

2. Change into the project directory:

   ```shell
   cd event-registration-system
   ```

3. Install the project dependencies:

   ```shell
   pip install -r requirements.txt
   ```

4. Configure the database settings in the `settings.py` file.

5. Apply database migrations:

   ```shell
   python manage.py migrate
   ```

6. Start the development server:

   ```shell
   python manage.py runserver
   ```

7. Access the application in your browser at `http://localhost:8000`.

## API Documentation

The API documentation provides detailed information about the available endpoints and their usage. Please refer to the [API Documentation](API_DOCUMENTATION.md) file for more information.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow the guidelines in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)