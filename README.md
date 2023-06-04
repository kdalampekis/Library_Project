# Library_Project
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

Use `pip3 install <package_name>` to install each individual Python package (library) directly for the entire system, or create a virtual environment with the [`venv`](https://docs.python.org/3/library/venv.html) module. The necessary packages for this app are listed in `requirements.txt` and can be installed all together via `pip install -r requirements.txt`.


## Project Structure

Generally, Flask allows some freedom of choice regarding the layout of the application's components. This demo follows the structure recommended by the [official documentation](https://flask.palletsprojects.com/en/2.0.x/tutorial/layout/), whereby a package, arbitrarily named "`dbdemo`", contains the application's code and files, separated into folders for each category (models, controllers, HTML templates - views, static files such as css or images).

Additionally, it utilizes Blueprints, a Flask structure that divides the app into sub-modules. Each of those is supposed to represent an entity of the database, and contains its own __init__ file, and corresponding form and route declarations.

 - `__init__.py` configures the application, including the necessary information and credentials for the database
 - Each module folder contains:
    - an `__init__` file that initializes the Blueprint
    - a `routes.py` file with the relevant endpoints and corresponding controllers
 - `run.py` launches the simple, built-in server and runs the app on it
 - all HTML templates are stored together in the `templates` folder, but could also be separated per Blueprint

Run via the `flask run` command (set the environment variable `FLASK_APP` to `run.py`) or directly with `run.py`.

_The demo's toy database is created and populated by_ `db-project-demo.sql`.

## Good Practices

 1. Never upload passwords or API keys to github. One simple way to secure your passwords is to store them in a separate file, that will be included in `.gitignore`:

    _dbdemo/config.json_
    ```json
    {
        "MYSQL_USER": "dbuser",
        "MYSQL_PASSWORD": "dbpass",
        "MYSQL_DB": "dbname",
        "MYSQL_HOST": "localhost",
        "SECRET_KEY": "key",
        "WTF_CSRF_SECRET_KEY": "key"
    }
    ```
    Import the credentials in `__init__.py` by replacing the `app.config` commands with:
    ```python
    import json
    ## ...
    app.config.from_file("config.json", load = json.load)
    ```
    
## Note for Linux users

Applications that run without `sudo` privileges often are not allowed to connect to MySQL with the _root_ user. In order to overcome this problem, you should create a new MySQL user an grant him privileges for this demo application. Follow these steps:

1. Open a terminal and precede the `mysql` command with `sudo` to invoke it with the privileges of the root Ubuntu user in order to gain access to the root MySQL user. This can be done using  
`sudo mysql -u root -p`.
2. Create a new MySQL user using:  
`mysql> CREATE USER 'type_username'@'localhost' IDENTIFIED BY 'type_your_password_here_123';`
3. Grant the user root privileges on the application's database using:  
`mysql> GRANT ALL PRIVILEGES ON demo.* TO 'type_username'@'localhost' WITH GRANT OPTION;`
4. Reload the grant tables to ensure that the new privileges are put into effect using:
`FLUSH PRIVILEGES;`.
5. Exit MySQL with `mysql> exit;`.
7. Go to `dbdemo/__init__.py` and change the `app.config["MYSQL_USER"]` and `app.config["MYSQL_PASSWORD"]` lines according to the username and the password you chose before.

For more details read [this](https://www.digitalocean.com/community/tutorials/how-to-create-a-new-user-and-grant-permissions-in-mysql).
    

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


## License

This project is licensed under the [MIT License](LICENSE).

