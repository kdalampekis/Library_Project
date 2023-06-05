# Library_Project

# Project Participants
-	Anastasia Askouni 03120046
-	Konstantinos Dalampekis 03120055
-	Konstantinos Spiridonos 03120198

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

You can also download it as a zip and extract it in the desired directory, if that suits you better.

2. By running the DDL and DML files that you will find in directory sql scripts, create the database using a DBSM that supports MySQL/MariaDB.

Just one of the many ways to do that will be presented below.

Important! 
In our [__init__.py] file in the librarynetwork directory we have configured the database connection using “project” as the name of the database.
You can either create a “project” databse, or  if you choose a different name please update the following fragment of code in [__init__.py].

app.config["MYSQL_DB"] = ‘your_choice’

The suggested way(including XAMPP installation):

    2.1	Install XAMPP.

      2.2	Open XAMPP control pannel and start the Apache web server and MySQL database server. These should be started every time you want to run the application to ensure the database connection.

      2.3	The MySQL database management tool (phpMyAdmin) will be needed for the database creation. You can go there through the XAMPP control panel or by visiting  http://localhost/phpmyadmin directly.

      2.4	Click on "New" to create a new database. Concerning the database name please consult the Important! Section that was provided earlier.

      2.5	Then by using the “Import” functionality, you should run the DDL and DML scripts, in that order.

      2.6	Your database is created!

3. Let’s continue with the application setup. Get in the librarynetwork directory by executing the following command at your terminal:

```cd /your/path/librarynetwork```

where /your/path is the path to the directory you created before.


4. During this step you will create the virtual environment for the application. The command needed is:

```python -m venv venv```	or	```python3 -m venv venv```	

depending on your python version.


Wait a bit! That might take a moment.

Make sure that you have installed python and added the path correctly before.

5. After step 3, there should be a venv directory now inside the librarynetwork one. Let’s activate it by executing(in /your/path/librarynetwork):

```venv\Scripts\activate```

You can execute ```venv\Scripts\deactivate``` when to exit the virtual environment later.

6. Now you are ready to install all requirements. First go back to the initial directory by executing:

```cd ../```		or 		```cd /your/path``` (specific path needed)

and then:

```pip install -r requirements.txt```

Wait until all files are installed before going on to the next step.

7. You are ready to launch the application! Execute command (without changing directory from the initial):

```python run.py```	or	```python3 run.py```

depending on your python version.

You will be shown this message. 
```
* Serving Flask app 'librarynetwork' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://localhost:5000 (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 857-543-339
```
Visit `http://localhost:5000` and get started with exploring our application!

## License

This project is licensed under the [MIT License](LICENSE).


