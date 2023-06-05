from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.jinja_env.filters['zip'] = zip

# Configuration of the database
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = ''
app.config["MYSQL_DB"] = 'project'
app.config["MYSQL_HOST"] = 'localhost'
app.config["SECRET_KEY"] = 'key'

# Initialize MySQL
mysql = MySQL(app)

# Register the routes
from .routes import *

# a function that needed to be global
@app.context_processor
def inject_user_checks():
    def user_checks_before_serving(reservation_id):
        error_messages = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT User.*, Reservation.ISBN FROM Reservation JOIN User ON Reservation.user_id = User.user_id '
            'WHERE Reservation.reservation_id = %s', (reservation_id,))
        user_and_isbn = cursor.fetchone()
        cursor.execute('SELECT EXISTS'
                       '(SELECT 1 FROM Borrowing WHERE user_id = %s AND ISBN = %s AND borrowing_status IN (%s, %s)) '
                       'AS same_borrowing_exists', (user_and_isbn['user_id'], user_and_isbn['ISBN'], 'active', 'late'))
        same_borrowing_exists = cursor.fetchone()['same_borrowing_exists']
        cursor.execute('SELECT EXISTS(SELECT 1 FROM Borrowing WHERE user_id = %s AND borrowing_status = %s)'
                       'AS late_borrowing_exists', (user_and_isbn['user_id'], 'late'))
        late_borrowing_exists = cursor.fetchone()['late_borrowing_exists']
        cursor.close()
        if user_and_isbn['current_borrowings'] == 2 and user_and_isbn['user_type'] == 'student':
            error_messages.append('has started 2 borrowings this week and is a student')
        if user_and_isbn['current_borrowings'] == 2 and user_and_isbn['user_type'] == 'professor':
            error_messages.append('has started 1 borrowings this week and is a professor')
        if late_borrowing_exists:
            error_messages.append('late to return a borrowed book')
        if same_borrowing_exists:
            error_messages.append('has not returned this book yet')
        print(error_messages)
        return error_messages

    return dict(user_checks_before_serving=user_checks_before_serving)


