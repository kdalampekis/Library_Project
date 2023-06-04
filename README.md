# Library_Project
# Student Library Website

This is a web application built using Python, Flask, and HTML to create a student library website. The website allows students to browse and search for books, borrow and return books, and provides administrative features for library operators.

## Features

- User registration and login: Students can create an account and log in to the website to access the library features.
- Book catalog: Students can browse and search for books in the library catalog.
- Book details: Students can view detailed information about each book, including its title, author, description, and availability.
- Borrowing and returning books: Students can borrow books from the library and return them when they are finished.
- User dashboard: Students have a personal dashboard where they can view their borrowed books, due dates, and history.
- Administrative features: Library operators have access to administrative features like adding new books, managing book availability, and viewing borrowing statistics.

## Installation

1. Clone the repository:

git clone https://github.com/kdalampekis/student-library-website.git

2. Change into the project directory:

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

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

