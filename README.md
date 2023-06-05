# Library_Project

# Project Participants
Anastasia Askouni 03120046
Konstantinos Dalampekis 03120055
Konstantinos Spiridonos 03120198

# School Library Network in Public Schools

This is a web application built using Python, Flask, and HTML to create a School Library Network application.
The website allows users search for books and their details, reserve and review them, while providing administrative features for library operators.

## Features

- User registration and login: Students, Professors and Operators can create an account and log in to the website to access the library features.
- User profile: Users can view their personal information, digital library card, list of borrowings, reservations, reviews.
- Book catalogue: Users can browse and search for books in their school library catalogue.
- Book details: Users can view detailed information about each book, including its title, author, description, and availability.
- Reserving and reviewing books: Users can rserve books, so a borrowing can be registered later. They can also review them and edit their reviews.
- Administrative features: Library operators have access to administrative features like adding new books, editing existing books information, managing book availability, user accounts, and viewing borrowing statistics.

## Dependencies

 - [MySQL](https://www.mysql.com/) for Windows
 - [Python](https://www.python.org/downloads/), with the additional libraries:
    - [Flask](https://flask.palletsprojects.com/en/2.0.x/)
    - [Flask-MySQLdb](https://flask-mysqldb.readthedocs.io/en/latest/)
    - [faker](https://faker.readthedocs.io/en/master/) (for data generation)
    - [Flask-WTForms](https://flask-wtf.readthedocs.io/en/1.0.x/) and [email-validator](https://pypi.org/project/email-validator/) (a more involved method of input validation)

## Installation

1. The first thing you need to do is clone the repository in a local working directory:

git clone https://github.com/kdalampekis/student-library-website.git

2. Then change into /librarynetwork directory of:

cd student-library-website


3. Install the dependencies:

pip install -r requirements.txt


4. Set up the database:

- Create a MySQL database and update the database connection details in the `config.py` file.

- Run the following command to create the necessary database tables:

  ```
  python manage.py db upgrade
  ```

5. Start the application:

python app.py


The application will be accessible at `http://localhost:5000`.

## Usage

- Register a new account or log in with an existing account.

- Browse and search for books in the library catalog.

- View book details to see the availability and other information.

- Borrow books by clicking the "Borrow" button and return them using the "Return" button.

- Library operators can log in and access the administrative features from the dashboard.


## License

This project is licensed under the [MIT License](LICENSE).

