from flask import render_template, request, redirect, url_for, session, flash
import MySQLdb.cursors
from datetime import datetime
import subprocess
import re
from . import app, mysql

# home page
@app.route('/')
def home():
    return render_template('login.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not all([username, password]):
            message = 'Please fill in the fields.'
            return render_template('login.html', message=message)
        cursor.execute('SELECT * FROM User WHERE username = %s AND password = %s', (username, password,))
        user = cursor.fetchone()
        if user:
            session['user'] = user
            return redirect(url_for('userprofile'))
        else:
            cursor.close()
            message = "This set of username and password does not correspond to any existing account. Please try again."
    return render_template('login.html', message=message)


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not all([username, password]):
            message = 'Please fill in the fields.'
            return render_template('adminlogin.html', message=message)
        cursor.execute('SELECT * FROM Administrator WHERE admin_username = %s AND admin_password = %s', (username, password,))
        user = cursor.fetchone()
        if user:
            session['user'] = user
            return redirect(url_for('adminprofile'))
        else:
            cursor.close()
            message = "This set of username and password does not correspond to the administrator account. Please try again."
    return render_template('adminlogin.html', message=message)


@app.route("/logout")
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT school_name FROM School_Unit")
    school_units = cursor.fetchall()
    cursor.close()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        re_password = request.form['re-enter password']
        first_name = request.form['first name']
        last_name = request.form['last name']
        email = request.form['email']
        date_of_birth = request.form['date of birth']
        user_type = request.form['user type']
        school_unit = request.form['school unit']
        error_messages = []  # List to accumulate error messages

        if not all([username, password, re_password, first_name, last_name, email, date_of_birth])\
                or user_type == "click to select"\
                or school_unit == "click to select":
            error_messages.append('Please fill in all the required fields.')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = %s', (username,))
        existing_user = cursor.fetchone()
        cursor.close()
        if existing_user:
            error_messages.append('Username already exists. Please choose a different username.')

        if password != re_password:
            error_messages.append("Passwords didn't match.")

        if date_of_birth and user_type:
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
            current_date = datetime.now()
            age = current_date.year - date_of_birth.year
            if (user_type == 'student' and (age <= 5 or age >= 19)) or (user_type != 'student' and age < 22):
                error_messages.append("Please select valid date of birth according to the user type you have chosen.")

        if error_messages:
            return render_template('register.html', error_messages=error_messages, school_units=school_units)
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT school_id FROM School_Unit WHERE school_name = %s', (school_unit,))
            school = cursor.fetchone()

            insert_query = 'INSERT INTO User ' \
                           '(school_id, username, password, user_type, email, first_name, last_name, date_of_birth) ' \
                           'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(insert_query, (school['school_id'], username, password, user_type, email, first_name, last_name, date_of_birth))
            mysql.connection.commit()
            cursor.close()
            message = 'Successfully Registered. Please login with your credentials.'
            return render_template('register.html', message=message, school_units=school_units)
    return render_template('register.html', school_units=school_units)


@app.route('/adminprofile')
def adminprofile():
    if 'user' not in session:
        return redirect(url_for('adminlogin'))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Administrator ')
        user = cursor.fetchone()
        cursor.close()
        session['user']=user
        return render_template('adminprofile.html', user=user)


@app.route('/userprofile')
def userprofile():
    if 'user' not in session:
        return redirect(url_for('logout'))
    else:
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE user_id =  %s', (user['user_id'],))
        user = cursor.fetchone()
        cursor.execute('SELECT * FROM School_Unit WHERE school_id = %s', (user['school_id'],))
        school = cursor.fetchone()
        cursor.close()
        return render_template('userprofile.html', user=user, school=school)


@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    if 'user' not in session:
        return redirect(url_for('logout'))
    else:
        user = session.get('user')
        message = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE user_id =  %s', (user['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        if request.method == 'POST' and 'new_password' in request.form:
            new_password = request.form['new_password']
            if not new_password:
                message = 'Please type in a new password before pressing save.'
                return render_template('changepassword.html', user=user, message=message)
            user_id = session['user']['user_id']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE User SET password = %s WHERE user_id = %s', (new_password, user_id))
            mysql.connection.commit()
            cursor.close()
            session['user']['password'] = new_password
            user['password'] = new_password
            message = 'Your password has been succesfully changed.'
        return render_template('changepassword.html', user=user, message=message)


@app.route('/changeadmpassword', methods=['GET', 'POST'])
def changeadmpassword():
    if 'user' not in session:
        return redirect(url_for('logout'))
    else:
        user = session.get('user')
        username = user['admin_username']
        message = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Administrator WHERE admin_username =  %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        if request.method == 'POST' and 'new_password' in request.form:
            new_password = request.form['new_password']
            if not new_password:
                message = 'Please type in a new password before pressing save.'
                return render_template('changeadmnewpassword.html', user=user, message=message)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE Administrator SET admin_password = %s WHERE admin_username = %s', (new_password, username))
            mysql.connection.commit()
            cursor.close()
            session['user']['admin_password'] = new_password
            user['admin_password'] = new_password
            message = 'Your password has been succesfully changed.'
        return render_template('changeadmnewpassword.html', user=user, message=message)


@app.route('/myreservations')
def myreservations():
    if 'user' not in session:
        return redirect(url_for('logout'))
    else:
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Reservation JOIN Book ON Reservation.ISBN = Book.ISBN '
                       'WHERE Reservation.user_id = %s ORDER BY Reservation.date_made desc', (user['user_id'],))
        reservations = cursor.fetchall()
        cursor.close()
        return render_template('myreservations.html', reservations=reservations)


@app.route('/cancel_reservation/<reservation_id>')
def cancel_reservation(reservation_id):
    if 'user' not in session:
        return redirect(url_for('logout'))
    else:
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Reservation SET reservation_status = %s WHERE reservation_id = %s',
               ('cancelled', reservation_id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('myreservations', user=user))


@app.route('/myborrowings')
def myrborrowings():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Borrowing JOIN Book ON Borrowing.ISBN = Book.ISBN '
                       'WHERE Borrowing.user_id = %s'
                       ' ORDER BY Borrowing.starting_date DESC', (user['user_id'],))
        borrowings = cursor.fetchall()
        cursor.close()
        return render_template('myborrowings.html', borrowings = borrowings)


@app.route('/myreviews')
def myreviews():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT Reviews.*, Book.title '
                       'FROM Reviews JOIN Book ON Reviews.ISBN = Book.ISBN '
                       'WHERE Reviews.user_id = %s ORDER BY '
                       '   CASE '
                       '       WHEN Reviews.publication_status = "written" THEN 1 '
                       '       WHEN Reviews.publication_status = "published" THEN 2 '
                       '       WHEN Reviews.publication_status = "declined" THEN 3 '
                       '   END', (user['user_id'],))
        reviews = cursor.fetchall()
        cursor.close()
        session['reviews'] = reviews
        return render_template('myreviews.html', reviews=reviews)


@app.route('/edit_review/<review_isbn>', methods=['GET', 'POST'])
def edit_review(review_isbn):
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        message = ''
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT Reviews.*, Book.title '
                       'FROM Reviews JOIN Book ON Reviews.ISBN = Book.ISBN '
                       'WHERE Reviews.user_id = %s AND Book.ISBN = %s ORDER BY '
                       '   CASE '
                       '       WHEN Reviews.publication_status = "written" THEN 1 '
                       '       WHEN Reviews.publication_status = "published" THEN 2 '
                       '       WHEN Reviews.publication_status = "declined" THEN 3 '
                       '   END', (user['user_id'], review_isbn))
        review = cursor.fetchone()
        cursor.close()
        if request.method == 'POST':
            new_likert_value = request.form.get('likert_value')
            if not new_likert_value:
                new_likert_value = None
            else:
                new_likert_value = int(new_likert_value)
            new_free_text = request.form['free_text']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if not any([new_likert_value, new_free_text]):
                message = 'Please provide both a rating and a free text for your review.'
                return render_template('edit_review.html', review=review, message=message)
            if new_likert_value:
                cursor.execute('UPDATE Reviews SET likert_value = %s, publication_status = "written"'
                               'WHERE user_id = %s', (new_likert_value, user['user_id']))
                review['likert_value'] = new_likert_value
            if new_free_text:
                cursor.execute('UPDATE Reviews SET free_text = %s, publication_status = "written"'
                               'WHERE user_id = %s', (new_free_text, user['user_id']))
                review['free_text'] = new_free_text
            mysql.connection.commit()
            cursor.close()
            message = 'Your review has been successfully edited.'
        return render_template('edit_review.html', review=review, message=message)


@app.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user = session.get('user')
        user['date_of_birth'] = datetime.strptime(user['date_of_birth'], '%a, %d %b %Y %H:%M:%S %Z').date()
        message = ''
        if request.method == 'POST':
            new_username = request.form['username']
            new_first_name = request.form['first_name']
            new_last_name = request.form['last_name']
            new_email = request.form['email']
            new_date_of_birth = request.form['date_of_birth']
            user_id = session['user']['user_id']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if not any(new_username or new_first_name or new_last_name or new_email or new_date_of_birth):
                message = 'No changes were made.'
                return render_template('editprofile.html', user=user, message=message)
            if new_username:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM User WHERE username = %s', (new_username,))
                existing_user = cursor.fetchone()
                cursor.close()
                if existing_user:
                   message = 'Username already exists. Please choose a different username.'
                   return render_template('editprofile.html', user=user, message=message)
                else:
                    cursor.execute('UPDATE User SET username = %s WHERE user_id = %s', (new_username, user_id))
                    user['username'] = new_username
            if new_first_name:
                cursor.execute('UPDATE User SET first_name = %s WHERE user_id = %s', (new_first_name, user_id))
                user['first_name'] = new_first_name
            if new_last_name:
                cursor.execute('UPDATE User SET last_name = %s WHERE user_id = %s', (new_last_name, user_id))
                user['last_name'] = new_last_name
            if new_email:
                cursor.execute('UPDATE User SET email = %s WHERE user_id = %s', (new_email, user_id))
                user['email'] = new_email
            if new_date_of_birth:
                cursor.execute('UPDATE User SET date_of_birth = %s WHERE user_id = %s', (new_date_of_birth, user_id))
                user['date_of_birth'] = new_date_of_birth
            mysql.connection.commit()
            cursor.close()
            message = 'Your personal data has been successfully changed.'
        return render_template('editprofile.html', user=user, message=message)

@app.route('/userhome')
def userhome():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    return render_template('userhome.html', user=user)


@app.route('/myborrowinglist')
def myborrowinglist():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # query for 3.3.2
    query = '''
        SELECT ISBN, title
        FROM Book
        WHERE ISBN IN (
            SELECT ISBN
            FROM Borrowing
            WHERE user_id = %s
        )
    '''
    cursor.execute(query, (user['user_id'],))
    books = cursor.fetchall()
    cursor.close()
    return render_template('myborrowinglist.html', user=user, books=books)


@app.route('/booklist', methods=['GET', 'POST'])
def booklist():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    school_id = user.get('school_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''
        SELECT Book.title, GROUP_CONCAT(Book_author.author) AS authors, GROUP_CONCAT(Book_thematic_category.thematic_category) AS categories
        FROM Book
        JOIN Belongs_to ON Book.ISBN = Belongs_to.ISBN
        JOIN Book_author ON Book.ISBN = Book_author.ISBN
        JOIN Book_thematic_category ON Book.ISBN = Book_thematic_category.ISBN
        WHERE Belongs_to.school_id = %s
        GROUP BY Book.ISBN;
    '''
    cursor.execute(query, (school_id,))
    searches = cursor.fetchall()
    titles = sorted(list(set(search['title'] for search in searches)))  # Get unique titles and sort alphabetically
    authors = sorted(list(set(author for search in searches for author in
                              search['authors'].split(','))))  # Get unique authors and sort alphabetically
    categories = sorted(list(set(category for search in searches for category in
                                 search['categories'].split(','))))  # Get unique categories and sort alphabetically
    cursor.close()
    if request.method == 'POST':
        if user['user_type'] == 'operator':
            # query for 3.2.1
            search_title = request.form.get('title', None)
            search_author = request.form.get('author', None)
            search_category = request.form.get('category', None)
            search_copies = request.form.get('copies', '')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = '''
                SELECT b.title, b.cover_image, b.ISBN,
                    (SELECT GROUP_CONCAT(DISTINCT ba.author) FROM Book_author ba WHERE ba.ISBN = b.ISBN) AS authors
                FROM Book b
                WHERE
                    (b.title = %s OR %s IS NULL)
                    AND (%s IS NULL OR EXISTS (
                        SELECT 1 FROM Book_author ba WHERE ba.ISBN = b.ISBN AND ba.author = %s
                    ))
                    AND (%s IS NULL OR EXISTS (
                        SELECT 1 FROM Book_thematic_category bt WHERE bt.ISBN = b.ISBN AND bt.thematic_category = %s
                    ))
                    AND (b.ISBN IN (
                        SELECT bc.ISBN FROM Belongs_to bc WHERE bc.school_id = %s AND 
                        (bc.copies_available = %s OR %s ='')
                    ))
                ORDER BY b.title;
            '''
            cursor.execute(query, (search_title, search_title, search_author, search_author,
                                search_category, search_category, school_id, search_copies, search_copies))
            books = cursor.fetchall()
            return render_template('booklist.html', books=books, titles=titles, authors=authors, categories=categories, user=user)
        else:
            search_title = request.form.get('title', None)
            search_author = request.form.get('author', None)
            search_category = request.form.get('category', None)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # query for 3.3.1
            query = '''
                SELECT b.title, b.cover_image, b.ISBN,
                    (SELECT GROUP_CONCAT(DISTINCT ba.author) FROM Book_author ba WHERE ba.ISBN = b.ISBN) AS authors
                FROM Book b
                WHERE
                    (b.title = %s OR %s IS NULL)
                    AND (%s IS NULL OR EXISTS (
                        SELECT 1 FROM Book_author ba WHERE ba.ISBN = b.ISBN AND ba.author = %s
                    ))
                    AND (%s IS NULL OR EXISTS (
                        SELECT 1 FROM Book_thematic_category bt WHERE bt.ISBN = b.ISBN AND bt.thematic_category = %s
                    ))
                    AND (b.ISBN IN (
                        SELECT bc.ISBN FROM Belongs_to bc WHERE bc.school_id = %s
                    ))
                ORDER BY b.title;
            '''
            cursor.execute(query, (search_title, search_title, search_author, search_author,
                                   search_category, search_category, school_id))
            books = cursor.fetchall()
            return render_template('booklist.html', books=books, titles=titles, authors=authors, categories=categories, user=user)
    return render_template('booklist.html', titles=titles, authors=authors, categories=categories, user=user)


@app.route('/bookforuser/<book_isbn>')
def bookforuser(book_isbn):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    error_messages = []
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT current_reservations FROM User WHERE user_id =  %s', (user['user_id'],))
    curr_reserv = cursor.fetchone()
    cursor.close()
    if curr_reserv['current_reservations'] == 2 and user['user_type'] == 'student':
        error_messages.append('You have already made 2 reservations this week.')
    if curr_reserv['current_reservations'] == 1 and user['user_type'] == 'professor':
        error_messages.append('You have already made 1 reservation this week.')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Borrowing WHERE user_id=  %s AND borrowing_status="late"', (user['user_id'],))
    late_borrow = cursor.fetchone()
    cursor.close()
    if late_borrow:
        error_messages.append('You are late to return a borrowed book.')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Borrowing WHERE user_id= %s AND ISBN=%s AND borrowing_status IN (%s, %s)', (user['user_id'], book_isbn, 'active', 'late'))
    active_borrow = cursor.fetchone()
    cursor.close()
    if active_borrow:
        error_messages.append('You have not yet completed a borrowing of this book.')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Reservation WHERE ISBN = %s and reservation_status IN (%s, %s) and user_id=  %s', (book_isbn,'made', 'on hold', user['user_id'],))
    already_reserv = cursor.fetchone()
    cursor.close()
    if already_reserv:
        error_messages.append('You have already reserved this book.')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT Book.*, 
               (SELECT GROUP_CONCAT( author) FROM Book_author WHERE Book_author.ISBN = Book.ISBN) AS authors,
               (SELECT GROUP_CONCAT( thematic_category) FROM Book_thematic_category WHERE Book_thematic_category.ISBN = Book.ISBN) AS thematic_categories,
               (SELECT GROUP_CONCAT( keyword) FROM Book_keyword WHERE Book_keyword.ISBN = Book.ISBN) AS keywords,
               Belongs_to.copies_available
        FROM Book
        JOIN Belongs_to ON Book.ISBN = Belongs_to.ISBN
        WHERE Book.ISBN = %s AND Belongs_to.school_id = %s
    ''', (book_isbn, user['school_id']))
    book = cursor.fetchone()

    cursor.execute('''
    SELECT Reviews.*, User.username
    FROM Reviews
    JOIN User ON Reviews.user_id = User.user_id
    WHERE Reviews.ISBN = %s and Reviews.publication_status = 'published' and User.school_id = %s
    ''', (book_isbn, user['school_id']))
    reviews = cursor.fetchall()

    cursor.execute('''
        SELECT * FROM Reviews
        WHERE Reviews.ISBN = %s and Reviews.publication_status != 'declined' and Reviews.user_id = %s
        ''', (book_isbn, user['user_id']))
    user_rev = cursor.fetchone()
    cursor.close()
    session['book'] = book
    return render_template('bookforuser.html', book=book, reviews=reviews, user=user, user_rev=user_rev, error_messages = error_messages)


@app.route('/user_review/<book_isbn>', methods=['GET', 'POST'])
def user_review(book_isbn):
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT *FROM Book WHERE ISBN =  %s', (book_isbn,))
        book = cursor.fetchone()
        cursor.close()
        message = ''
        if request.method == 'POST':
            likert_value = request.form.get('likert_value')
            if not likert_value:
                likert_value = None
            else:
                likert_value = int(likert_value)
            free_text = request.form['free_text']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if not all([likert_value, free_text]):
                message = 'Please provide both a rating and a free text for your review.'
                return render_template('user_review.html', book=book, message=message)
            cursor.execute('''
                INSERT INTO Reviews (ISBN, user_id, free_text, likert_value)
                VALUES (%s, %s, %s, %s)
            ''', (book_isbn, user['user_id'], free_text, likert_value))
            mysql.connection.commit()
            cursor.close()
            message ='Your review has been successfully registered.'
    return render_template('user_review.html', book=book, message=message)


@app.route('/user_reserve/<book_isbn>')
def user_reserve(book_isbn):
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        current_date = datetime.now().date()
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO Reservation (ISBN, user_id, date_made) VALUES (%s, %s, %s)',
                       (book_isbn, user['user_id'], current_date))
        mysql.connection.commit()
        cursor.close()
        flash('A reservation has been succesfully made!', 'success')
        return redirect(url_for('bookforuser', book_isbn=book_isbn))


@app.route('/operatorhome')
def operatorhome():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM school_unit WHERE school_id = %s', (user['school_id'],))
    school = cursor.fetchone()
    cursor.close()
    session['school'] = school
    return render_template('operator.html', user=user, school=school)


@app.route('/userlist')
def userlist():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM User WHERE school_id = %s AND account_status = %s AND user_type!=%s',
                   (user['school_id'], 'pending', 'operator'))
    pending_users = cursor.fetchall()
    cursor.execute('SELECT * FROM User WHERE school_id = %s AND account_status = %s AND user_type!=%s',
                   (user['school_id'], 'registered', 'operator'))
    registered_users = cursor.fetchall()
    cursor.execute('SELECT * FROM User WHERE school_id = %s AND account_status = %s AND user_type!=%s',
                   (user['school_id'], 'disabled', 'operator'))
    disabled_users = cursor.fetchall()
    cursor.close()
    return render_template('userlist.html', user=user, pending_users=pending_users, registered_users=registered_users, disabled_users=disabled_users)


@app.route('/operatorslist')
def operatorslist():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM User WHERE  account_status = %s AND user_type = %s',
                   ('pending', 'operator'))
    pending_users = cursor.fetchall()
    cursor.execute('SELECT * FROM User WHERE  account_status = %s AND user_type = %s',
                   ('registered', 'operator'))
    registered_users = cursor.fetchall()
    cursor.execute('SELECT * FROM User WHERE  account_status = %s AND user_type = %s',
                   ('disabled', 'operator'))
    disabled_users = cursor.fetchall()
    cursor.close()
    return render_template('operatorslist.html', user=user, pending_users=pending_users, registered_users=registered_users, disabled_users=disabled_users)



@app.route('/userlistprofile/<view_id>')
def userlistprofile(view_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE user_id =  %s', (view_id,))
        view_user = cursor.fetchone()
        cursor.execute('SELECT * FROM School_Unit WHERE school_id = %s', (user['school_id'],))
        school = cursor.fetchone()
        cursor.close()
        return render_template('userlistprofile.html', user=user, view_user=view_user, school=school)


@app.route('/operatorslistprofile/<view_id>')
def operatorslistprofile(view_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user = session.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE user_id =  %s', (view_id,))
        view_user = cursor.fetchone()
        cursor.execute('SELECT school_name FROM School_Unit WHERE school_id =  %s', (view_user['school_id'],))
        school = cursor.fetchone()
        cursor.close()
        return render_template('operatorslistprofile.html', user=user, view_user=view_user, school=school)


@app.route('/register_user/<user_id>')
def register_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE User SET account_status = %s WHERE user_id = %s', ('registered', user_id))
    mysql.connection.commit()
    cursor.close()
    flash('User was successfully registered.', 'success')
    return redirect(url_for('userlist'))

@app.route('/disable_user/<user_id>')
def disable_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE User SET account_status = %s, current_reservations = 0, current_borrowings =0'
                   ' WHERE user_id = %s', ('disabled', user_id))
    mysql.connection.commit()
    cursor.close()
    flash('User was successfully disabled.', 'success')
    return redirect(url_for('userlist'))

@app.route('/delete_user/<user_id>')
def delete_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM User WHERE user_id = %s', ( user_id,))
    mysql.connection.commit()
    cursor.close()
    flash('User was successfully deleted.', 'success')
    return redirect(url_for('userlist'))


@app.route('/editbook', methods=['GET', 'POST'])
def editbook():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        book = session.get('book')
        author_list = book['authors'].split(',')
        category_list = book['thematic_categories'].split(',')
        keyword_list = book['keywords'].split(',')
        message = ''
        if request.method == 'POST':
            new_title = request.form['title']
            new_publisher = request.form['publisher']
            new_page_number = request.form['page_number']
            new_summary = request.form['summary']
            new_language = request.form['language']
            new_cover_image = request.form['cover_image']
            new_copies_available = request.form['copies_available']
            new_authors = request.form.getlist('new_author[]')  # Get the list of new authors
            new_thematic_categories = request.form.getlist('new_category[]')
            new_keywords = request.form.getlist('new_keyword[]')

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if not all([new_authors, new_thematic_categories, new_keywords]):
                message = 'There has to be at least one author, one thematic category and one keyword.'
                return render_template('editbook.html', book=book, message=message)

            if (author_list == new_authors and category_list == new_thematic_categories and keyword_list == new_keywords
                    and not any(new_title or new_publisher or new_page_number or new_summary or new_language or new_cover_image or new_copies_available)):
                message = 'No changes were made.'
                return render_template('editbook.html', book=book, message=message)

            if new_title:
                cursor.execute('UPDATE Book SET title = %s WHERE ISBN = %s', (new_title, book['ISBN']))
                book['title'] = new_title
            if new_publisher:
                cursor.execute('UPDATE Book SET publisher = %s WHERE ISBN = %s', (new_publisher, book['ISBN']))
                book['publisher'] = new_publisher
            if new_page_number:
                cursor.execute('UPDATE Book SET page_number = %s WHERE ISBN = %s', (new_page_number, book['ISBN']))
                book['page_number'] = new_page_number
            if new_summary:
                cursor.execute('UPDATE Book SET summary = %s WHERE ISBN = %s', (new_summary, book['ISBN']))
                book['summary'] = new_summary
            if new_language:
                cursor.execute('UPDATE Book SET language = %s WHERE ISBN = %s', (new_language, book['ISBN']))
                book['language'] = new_language
            if new_cover_image:
                cursor.execute('UPDATE Book SET cover_image = %s WHERE ISBN = %s', (new_cover_image, book['ISBN']))
                book['cover_image'] = new_cover_image
            if new_copies_available:
                cursor.execute('UPDATE Belongs_to SET copies_available = %s WHERE ISBN = %s', (new_copies_available, book['ISBN']))
                book['copies_available'] = new_copies_available

            # Update authors
            if any(author.strip() for author in new_authors):
                # Delete existing authors for the book
                cursor.execute('DELETE FROM book_author WHERE ISBN = %s', (book['ISBN'],))
                # Insert new authors
                for author in new_authors:
                    author = author.strip()
                    cursor.execute('INSERT INTO book_author (ISBN, author) VALUES (%s, %s)', (book['ISBN'], author))
                book['authors'] = ', '.join(new_authors)


            # Update thematic categories
            if any(category.strip() for category in new_thematic_categories):
                # Delete existing categories for the book
                cursor.execute('DELETE FROM book_thematic_category WHERE ISBN = %s', (book['ISBN'],))
                # Insert new categories
                for category in new_thematic_categories:
                    category = category.strip()  # Remove leading/trailing whitespace
                    cursor.execute('INSERT INTO book_thematic_category (ISBN, thematic_category) VALUES (%s, %s)', (book['ISBN'], category))
                book['thematic_categories'] = ', '.join(new_thematic_categories)

            # Update keywords
            if any(keyword.strip() for keyword in new_keywords):
                # Delete existing keywords for the book
                cursor.execute('DELETE FROM book_keyword WHERE ISBN = %s', (book['ISBN'],))
                # Insert new keywords
                for keyword in new_keywords:
                    keyword = keyword.strip()  # Remove leading/trailing whitespace
                    cursor.execute('INSERT INTO book_keyword (ISBN, keyword) VALUES (%s, %s)', (book['ISBN'], keyword))
                book['keywords'] = ', '.join(new_keywords)

            mysql.connection.commit()
            cursor.close()
            message = 'Book details have been successfully updated.'
            session['book']=book
        return render_template('editbook.html', book=book, message=message)

@app.route('/addbook', methods=['GET', 'POST'])
def addbook():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user=session.get('user')
        message = ''
        if request.method == 'POST':
            new_isbn = request.form['ISBN']
            new_title = request.form['title']
            new_publisher = request.form['publisher']
            new_page_number = request.form['page_number']
            new_summary = request.form['summary']
            new_language = request.form['language']
            new_cover_image = request.form['cover_image']
            new_copies_available = request.form['copies_available']
            new_authors = request.form.getlist('new_author[]')  # Get the list of new authors
            new_thematic_categories = request.form.getlist('new_category[]')
            new_keywords = request.form.getlist('new_keyword[]')

            if not all([new_isbn, new_title, new_publisher, new_page_number, new_summary, new_language,
                        new_cover_image, new_copies_available, new_authors, new_thematic_categories, new_keywords]):
                message = 'All fields are required bor the book insertion.'
                return render_template('addbook.html', message=message)

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            insert_query = 'INSERT INTO Book (ISBN, title, publisher, page_number, summary, cover_image, language)' \
                           'VALUES (%s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(insert_query,
                           (new_isbn, new_title, new_publisher, new_page_number, new_summary, new_cover_image, new_language))
            cursor.execute('INSERT INTO Belongs_to (school_id, ISBN, copies_available) VALUES (%s, %s, %s)',
                           (user['school_id'], new_isbn, new_copies_available))
            for author in new_authors:
                cursor.execute('INSERT INTO book_author (author, ISBN) VALUES (%s, %s)', (author,new_isbn))
            for category in new_thematic_categories:
                cursor.execute('INSERT INTO book_thematic_category (thematic_category, ISBN) VALUES (%s, %s)', (category, new_isbn))
            for keyword in new_keywords:
                cursor.execute('INSERT INTO book_keyword (keyword, ISBN) VALUES (%s, %s)', (keyword,new_isbn))
            mysql.connection.commit()
            cursor.close()
            message = 'Book has been successfully added to the school book catalogue.'
        return render_template('addbook.html', user=user, message=message)


@app.route('/reservationlist')
def reservationlist():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT Reservation.*, User.school_id, User.username, Book.title FROM Reservation '
                   'JOIN User ON Reservation.user_id = User.user_id '
                   'JOIN Book ON Reservation.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND reservation_status = %s '
                   'ORDER BY Reservation.date_made DESC',
                   (user['school_id'], 'made'))
    made=cursor.fetchall()
    cursor.execute('SELECT Reservation.*, User.school_id, User.username, Book.title FROM Reservation '
                   'JOIN User ON Reservation.user_id = User.user_id '
                   'JOIN Book ON Reservation.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND reservation_status = %s '
                   'ORDER BY Reservation.date_made DESC',
                   (user['school_id'], 'on hold'))
    on_hold = cursor.fetchall()
    cursor.execute('SELECT Reservation.*, User.school_id, User.username, Book.title FROM Reservation '
                   'JOIN User ON Reservation.user_id = User.user_id '
                   'JOIN Book ON Reservation.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND reservation_status = %s '
                   'ORDER BY Reservation.date_made DESC',
                   (user['school_id'], 'served'))
    served = cursor.fetchall()
    cursor.close()
    return render_template('reservationlist.html', user=user, made=made, on_hold=on_hold, served=served)


@app.route('/serve_reservation/<reservation_id>')
def serve_reservation(reservation_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE Reservation '
                   'SET reservation_status = %s '
                   'WHERE reservation_id = %s',
                   ('served', reservation_id))
    mysql.connection.commit()
    cursor.close()
    flash('Borrowing has successfully started.', 'success')
    return redirect(url_for('reservationlist'))

@app.route('/borrowinglist')
def borrowinglist():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT Borrowing.*, User.school_id, User.username, Book.title FROM Borrowing '
                   'JOIN User ON Borrowing.user_id = User.user_id '
                   'JOIN Book ON Borrowing.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND borrowing_status = %s '
                   'ORDER BY Borrowing.starting_date DESC',
                   (user['school_id'], 'active'))
    activeb=cursor.fetchall()
    cursor.execute('SELECT Borrowing.*, User.school_id, User.username, Book.title FROM Borrowing '
                   'JOIN User ON Borrowing.user_id = User.user_id '
                   'JOIN Book ON Borrowing.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND borrowing_status = %s '
                   'ORDER BY Borrowing.starting_date DESC',
                   (user['school_id'], 'late'))
    lateb=cursor.fetchall()
    cursor.execute('SELECT Borrowing.*, User.school_id, User.username, Book.title FROM Borrowing '
                   'JOIN User ON Borrowing.user_id = User.user_id '
                   'JOIN Book ON Borrowing.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND borrowing_status = %s '
                   'ORDER BY Borrowing.starting_date DESC',
                   (user['school_id'], 'completed'))
    completedb=cursor.fetchall()
    cursor.execute('SELECT Borrowing.*, User.school_id, User.username, Book.title FROM Borrowing '
                   'JOIN User ON Borrowing.user_id = User.user_id '
                   'JOIN Book ON Borrowing.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND borrowing_status = %s '
                   'ORDER BY Borrowing.starting_date DESC',
                   (user['school_id'], 'completed late'))
    completed_lateb = cursor.fetchall()
    cursor.close()
    return render_template('borrowinglist.html', user=user, activeb=activeb, lateb=lateb,
                           completedb=completedb, completed_lateb=completed_lateb)

@app.route('/return_borrowing/<borrowing_id>')
def return_borrowing(borrowing_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE Borrowing '
                   'SET return_date = CURRENT_DATE '
                   'WHERE borrowing_id = %s',
                   (borrowing_id, ))
    mysql.connection.commit()
    cursor.close()
    flash('Borrowed book has been successfully returned.', 'success')
    return redirect(url_for('borrowinglist'))


@app.route('/reviewlist')
def reviewlist():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT Reviews.*, User.school_id, User.username, Book.title FROM Reviews '
                   'JOIN User ON Reviews.user_id = User.user_id '
                   'JOIN Book ON Reviews.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND publication_status = %s ',
                   (user['school_id'], 'written'))
    written = cursor.fetchall()
    cursor.execute('SELECT Reviews.*, User.school_id, User.username, Book.title FROM Reviews '
                   'JOIN User ON Reviews.user_id = User.user_id '
                   'JOIN Book ON Reviews.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND publication_status = %s ',
                   (user['school_id'], 'published'))
    published = cursor.fetchall()
    cursor.execute('SELECT Reviews.*, User.school_id, User.username, Book.title FROM Reviews '
                   'JOIN User ON Reviews.user_id = User.user_id '
                   'JOIN Book ON Reviews.ISBN = Book.ISBN '
                   'WHERE school_id = %s AND publication_status = %s ',
                   (user['school_id'], 'declined'))
    declined = cursor.fetchall()
    cursor.close()
    return render_template('reviewslist.html', user=user, written=written, published=published, declined=declined)


@app.route('/publish_review/<review_isbn>/<review_user_id>')
def publish_review(review_isbn, review_user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE Reviews '
                   'SET publication_status = %s '
                   'WHERE ISBN = %s AND user_id = %s',
                   ('published', review_isbn, review_user_id))
    mysql.connection.commit()
    cursor.close()
    flash('Review has been successfully published', 'success')
    return redirect(url_for('reviewlist'))


@app.route('/decline_review/<review_isbn>/<review_user_id>')
def decline_review(review_isbn, review_user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE Reviews '
                   'SET publication_status = %s '
                   'WHERE ISBN = %s AND user_id = %s',
                   ('declined', review_isbn, review_user_id))
    mysql.connection.commit()
    cursor.close()
    flash('Review has been successfully declined', 'success')
    return redirect(url_for('reviewlist'))

@app.route('/latetoreturn', methods=['GET', 'POST'])
def latetoreturn():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    school_id = user.get('school_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''
        SELECT first_name, last_name
        FROM User
        WHERE school_id = %s
    '''
    cursor.execute(query, (school_id,))
    searches = cursor.fetchall()
    firsts = sorted(list(set(search['first_name'] for search in searches)))
    lasts = sorted(list(set(search['last_name'] for search in searches)))
    cursor.close()

    if request.method == 'POST':
        search1 = request.form.get('first', '')
        search2 = request.form.get('last', '')
        search3 = request.form.get('days')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # query for 3.2.2
        query = '''
SELECT U.user_id, U.username, U.first_name, U.last_name, U.school_id, DATEDIFF(NOW(), B.expected_return) AS days
FROM User U
         INNER JOIN Borrowing B ON U.user_id = B.user_id
WHERE B.borrowing_status = 'late'
  AND (first_name = % s OR % s = '')
  AND (last_name = % s OR % s = '')
  AND (DATEDIFF(NOW(), B.expected_return) = % s OR % s = '')
  AND school_id = % s;
        '''
        cursor.execute(query, (search1, search1, search2, search2, search3, search3, school_id))
        late_users = cursor.fetchall()
        cursor.close()
        return render_template('latetoreturn.html', user=user, firsts=firsts, lasts=lasts, late_users=late_users)
    return render_template('latetoreturn.html', user=user, firsts=firsts, lasts=lasts)

@app.route('/reviewavr', methods=['GET', 'POST'])
def reviewavr():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    school_id = user.get('school_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''
        SELECT DISTINCT user_id
        FROM Borrowing
        WHERE user_id IN (
            SELECT user_id
            FROM User
            WHERE school_id = %s
        )
    '''
    cursor.execute(query, (school_id,))
    user_ids = [row['user_id'] for row in cursor.fetchall()]
    query = '''
        SELECT DISTINCT thematic_category
        FROM Book_thematic_category
        WHERE ISBN IN (SELECT ISBN FROM Belongs_to WHERE school_id = %s)
    '''
    cursor.execute(query, (school_id,))
    categories = [row['thematic_category'] for row in cursor.fetchall()]
    cursor.close()
    average=None
    if request.method == 'POST':
        user_id = request.form.get('user_id', '')
        category = request.form.get('category', '')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # query for 3.2.3
        query = '''
            SELECT FORMAT(AVG(r.likert_value), 2) AS average_likert_value
            FROM Reviews r
            JOIN (SELECT user_id, school_id FROM User) s ON r.user_id = s.user_id
            WHERE publication_status = 'published'
            AND (r.user_id = % s OR % s = '')
            AND (r.ISBN IN (SELECT btc.ISBN
                           FROM Book_thematic_category btc
                           WHERE btc.thematic_category = % s) OR % s = '')
            AND r.user_id IN (SELECT user_id FROM Borrowing)
            AND s.school_id = %s;
        '''
        cursor.execute(query, (user_id, user_id, category, category, school_id))
        average = cursor.fetchone()
        cursor.close()
        return render_template('reviewavr.html', user=user, user_ids=user_ids, categories=categories, average=average,
                               chosen_id=user_id,thematic_category=category)
    return render_template('reviewavr.html', user=user, user_ids=user_ids, categories=categories, average=average)


@app.route('/borrowregister', methods=['GET', 'POST'])
def borrowregister():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    school_id = user.get('school_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM User WHERE account_status = 'registered' AND school_id = %s AND "
        "(current_borrowings < 2 AND user_type = 'student' OR current_borrowings < 1 AND user_type = 'professor') AND "
        "user_id NOT IN (SELECT user_id FROM Borrowing WHERE borrowing_status = 'late')", (school_id,))
    borrowers = cursor.fetchall()
    session['borrowers'] = borrowers
    books = None
    borrower_id = None
    if request.method == 'POST':
        if 'user_id' in request.form:
            borrower_id = request.form.get('user_id')
            cursor.execute("SELECT Book.ISBN, Book.title FROM Book "
                        "JOIN Belongs_to ON Book.ISBN = Belongs_to.ISBN "
                        "WHERE Belongs_to.school_id = %s "
                        "AND Belongs_to.copies_available > 0 "
                        "AND Book.ISBN NOT IN "
                        "(SELECT ISBN FROM Borrowing WHERE user_id = %s AND borrowing_status = 'active')",
                        (school_id, borrower_id))
            books = cursor.fetchall()
            cursor.close()
            session['borrower_id'] = borrower_id
            return render_template('borrowregister.html', user=user, borrowers=borrowers, books=books,
                            selected_user_id=borrower_id)
    return render_template('borrowregister.html', user=user, borrowers=borrowers, books=books,
                            selected_user_id=borrower_id)


@app.route('/executeregister', methods=['POST'])
def executeregister():
    if 'user' not in session:
        return redirect(url_for('login'))
    borrower_id = session.get('borrower_id')
    borrowers = session.get('borrowers')
    if request.method == 'POST':
        if 'isbn' in request.form:
            message=''
            borrowing_book = request.form.get('isbn')
            current_date = datetime.now().date()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            insert_query = 'INSERT INTO Borrowing(user_id,ISBN,starting_date) VALUES (%s, %s, %s)'
            cursor.execute(insert_query, (borrower_id, borrowing_book, current_date))
            mysql.connection.commit()
            cursor.close()
            return render_template('borrowregister.html', selected_user_id=borrower_id, borrowing_book=borrowing_book,
                                   borrowers=borrowers, message=message)
        else:
            message='Please choose a Book.'
            return render_template('borrowregister.html', selected_user_id=borrower_id, borrowers=borrowers,
                                   message=message)


@app.route('/adminhome')
def adminhome():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    return render_template('adminhome.html', user=user)


@app.route('/schoollist', methods=['GET', 'POST'])
def schoollist():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''
        SELECT school_id, school_name, address,city, email, d_first_name, d_last_name, o_first_name, o_last_name FROM School_Unit;'''
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('schoollist.html', data=data)

@app.route('/edit/<school_id>', methods=['GET', 'POST'])
def editschool(school_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user=session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT * FROM School_Unit WHERE school_id = %s"
    cursor.execute(query, (school_id,))
    school = cursor.fetchone()
    cursor.close()
    message=''
    if request.method == 'POST':
        school_name = request.form['school_name']
        address = request.form['address']
        city = request.form['city']
        email = request.form['email']
        director_fn = request.form['d_first_name']
        director_ln = request.form['d_last_name']
        operator_fn = request.form['o_first_name']
        operator_ln = request.form['o_last_name']
        cursor = mysql.connection.cursor()
        if not any(school_name or address or city or email or director_fn or director_ln or operator_fn or operator_ln):
            message = 'No changes were made.'
            return render_template('editschool.html', user=user, school=school, message=message)
        if school_name:
            cursor.execute('UPDATE School_unit SET school_name = %s WHERE school_id = %s', (school_name, school['school_id']))
            school['school_name'] = school_name
        if address:
            cursor.execute('UPDATE School_unit SET address = %s WHERE school_id = %s', (address, school['school_id']))
            school['address'] = address
        if city:
            cursor.execute('UPDATE School_unit SET city = %s WHERE school_id = %s', (city, school['school_id']))
            school['city'] = city
        if email:
            cursor.execute('UPDATE School_unit SET email = %s WHERE school_id = %s', (email, school['school_id']))
            school['email'] = email
        if director_fn:
            cursor.execute('UPDATE School_unit SET d_first_name = %s WHERE school_id = %s', (director_fn, school['school_id']))
            school['d_first_name'] = director_fn
        if director_ln:
            cursor.execute('UPDATE School_unit SET d_last_name = %s WHERE school_id = %s', (director_ln, school['school_id']))
            school['d_last_name'] = director_ln
        if operator_fn:
            cursor.execute('UPDATE School_unit SET o_first_name = %s WHERE school_id = %s', (operator_fn, school['school_id']))
            school['o_first_name'] = operator_fn
        if operator_ln:
            cursor.execute('UPDATE School_unit SET o_last_name = %s WHERE school_id = %s', (operator_ln, school['school_id']))
            school['o_last_name'] = operator_ln
        mysql.connection.commit()
        cursor.close()
        message = 'School details have been successfully changed.'
    return render_template('editschool.html', school=school, user=user, message=message)


@app.route('/add_school', methods=['GET', 'POST'])
def add_school():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    message=''
    if request.method == 'POST':
        school_name = request.form['school_name']
        address = request.form['address']
        city = request.form['city']
        email = request.form['email']
        director_fn = request.form['d_first_name']
        director_ln = request.form['d_last_name']
        operator_fn = request.form['o_first_name']
        operator_ln = request.form['o_last_name']
        cursor = mysql.connection.cursor()
        if not all([school_name, address, city, email, director_fn, director_ln, operator_fn, operator_ln]):
            message = 'All fields are required bor the school unit insertion.'
            return render_template('add_school.html', message=message)
        query = '''
            INSERT INTO School_Unit (school_name, address, city, email,
            d_first_name, d_last_name, o_first_name, o_last_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (school_name, address, city, email, director_fn,
                               director_ln, operator_fn, operator_ln))
        mysql.connection.commit()
        cursor.close()
        message = 'School Unit has been successfully registered.'
    return render_template('add_school.html', user=user, message=message)

@app.route('/school_borrowings', methods=['GET', 'POST'])
def school_borrowings():
        if 'user' not in session:
            return redirect(url_for('login'))
        user = session.get('user')
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]
        current_year = datetime.now().year
        starting_year = 2000
        years = [str(year) for year in range(current_year, starting_year - 1, -1)]
        school_borrowings = None
        if request.method == 'POST':
            search_year = request.form.get('year', '')  # Get the search year from the form
            search_month = request.form.get('month', '')  # Get the search month from the form
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # query for 3.1.1
            query = '''
            SELECT SU.school_id, SU.school_name, COUNT(*) AS total_borrows
            FROM School_Unit SU
            JOIN (
                    SELECT user_id, school_id
                    FROM User
                    ) U ON SU.school_id = U.school_id
            JOIN Borrowing B ON U.user_id = B.user_id               
            WHERE (YEAR(B.starting_date) = %s OR %s = '')
            AND (MONTH(B.starting_date) = %s OR %s = '')
            GROUP BY SU.school_id, SU.school_name;
            '''
            cursor.execute(query, (search_year, search_year, search_month, search_month))
            school_borrowings = cursor.fetchall()
            cursor.close()
        return render_template('borrowingsperschool.html', user=user, school_borrowings=school_borrowings, months=months,
                               current_year=current_year, years=years)


@app.route('/authorsandprofessors', methods=['GET', 'POST'])
def authorsandprofessors():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT DISTINCT thematic_category FROM book_thematic_category;"
    cursor.execute(query)
    categories = cursor.fetchall()
    cursor.close()
    if request.method == 'POST':
        selected_category = request.form.get('category')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # query 1 for 3.1.2
        query_authors = '''
            SELECT author
            FROM book_author
            WHERE ISBN IN
            (SELECT ISBN FROM book_thematic_category WHERE thematic_category=%s);
        '''
        cursor.execute(query_authors, (selected_category,))
        authors = cursor.fetchall()
        # query 2 for 3.1.2
        query_professors = '''
        SELECT CONCAT(user.first_name,' ',user.last_name) AS 'professor' 
        FROM user
        INNER JOIN (SELECT user_id, ISBN, starting_date FROM borrowing) b ON user.user_id = b.user_id
        WHERE user_type='professor' AND
        ISBN IN (SELECT ISBN FROM book_thematic_category WHERE thematic_category=%s)
        AND YEAR(b.starting_date) = YEAR(CURDATE());'''
        cursor.execute(query_professors, (selected_category,))
        professors = cursor.fetchall()
        cursor.close()
        return render_template('authorsandprofessors.html', user=user, categories=categories, selected_category=selected_category, authors=authors, professors=professors)
    return render_template('authorsandprofessors.html', user=user, categories=categories)


@app.route('/youngprofessors', methods=['GET', 'POST'])
def youngprofessors():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # query for 3.1.3
    query = '''
        SELECT CONCAT(first_name, ' ', last_name) AS professor, total_borrowings
        FROM user
        JOIN (
        SELECT MAX(total_borrowings) AS max_borrowings
        FROM user
        WHERE user_type = 'professor'
        ) m ON user.total_borrowings = m.max_borrowings
        WHERE YEAR(date_of_birth) < YEAR(CURDATE()) - 40
        AND user_type = 'professor';
    '''
    cursor.execute(query)
    professors = cursor.fetchall()
    cursor.close()
    return render_template('youngprofessors.html', user=user, professors=professors)

@app.route('/authorswithoutbooks', methods=['GET', 'POST'])
def authorswithoutbooks():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # query for 3.1.4
    query = '''
        SELECT author
        FROM book_author
        WHERE ISBN NOT IN (SELECT DISTINCT ISBN FROM borrowing);
    '''
    cursor.execute(query)
    available_books = cursor.fetchall()
    cursor.close()
    return render_template('authorswithoutbooks.html', user=user, available_books=available_books)

@app.route('/operators_borrowings', methods=['GET', 'POST'])
def operators_borrowings():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    current_year = datetime.now().year
    starting_year = 2000
    years = [str(year) for year in range(current_year, starting_year - 1, -1)]
    message=''
    if request.method == 'POST':
        search_year = request.form.get('year', '')
        # query for 3.1.5
        query = '''
            SELECT GROUP_CONCAT(CONCAT(user.first_name,' ',user.last_name)) AS operators, result.total_b AS total_borrowings
            FROM user
            INNER JOIN ( SELECT u.school_id, COUNT(*) AS total_b FROM (SELECT school_id, user_id FROM User ) u
            INNER JOIN (SELECT starting_date, user_id FROM Borrowing) b ON u.user_id = b.user_id
            WHERE YEAR(B.starting_date) = %s OR %s = ''
            GROUP BY u.school_id
            HAVING COUNT(*) > 20
            ) AS result ON result.school_id = user.school_id
            WHERE user.user_type = 'operator'
            GROUP BY result.total_b
            HAVING COUNT(*) > 1;
        '''
        cursor.execute(query, (search_year, search_year))
        operators_borrowings = cursor.fetchall()
        cursor.close()
        if search_year =='':
            message = "Please choose a year"
        return render_template('sameoperatorborrowings.html', user=user, operators_borrowings=operators_borrowings, years=years, message=message)
    return render_template('sameoperatorborrowings.html', user=user, years=years)

@app.route('/top_thematic_combinations', methods=['GET', 'POST'])
def top_thematic_combinations():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # query for 3.1.6
    query = '''
SELECT thematic_category1, thematic_category2, COUNT(*) AS borrow_count
FROM (
    SELECT b1.thematic_category AS thematic_category1, b2.thematic_category AS thematic_category2
    FROM Book_thematic_category b1
    INNER JOIN Book_thematic_category b2 ON b1.ISBN = b2.ISBN AND b1.thematic_category < b2.thematic_category
    INNER JOIN (SELECT ISBN FROM Borrowing) bor ON b1.ISBN = bor.ISBN
) AS t
GROUP BY thematic_category1, thematic_category2
ORDER BY borrow_count DESC
LIMIT 3;
    '''
    cursor.execute(query)
    top_combinations = cursor.fetchall()
    cursor.close()
    return render_template('top3.html', user=user, top_combinations=top_combinations)

@app.route('/popular_authors', methods=['GET', 'POST'])
def popular_authors():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session.get('user')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''
    SELECT author, COUNT(*) AS book_count
    FROM Book_author
    GROUP BY author
    HAVING COUNT(*) + 5 <= (
    SELECT MAX(book_count)
    FROM (
        SELECT COUNT(*) AS book_count
        FROM Book_author
        GROUP BY author
    ) AS max_author_counts
);
    '''
    cursor.execute(query)
    popular_authors = cursor.fetchall()
    cursor.close()
    return render_template('5fewerbooks.html', user=user, popular_authors=popular_authors)


@app.route('/index', methods=['GET', 'POST'])
def index():
    message=''
    if request.method == 'POST':
        if 'backup' in request.form:
            backup_result = backup_database()
            if backup_result == 0:
                message = 'Backup was successful!'
            else:
                message = 'Backup failed.'
            return render_template('db_actions.html', message=message)
        elif 'restore' in request.form:
            restore_result = restore_database()
            if restore_result == 0:
                message = 'Database restored successfully!'
            else:
                message = 'Database restoration failed.'
            return render_template('db_actions.html', message=message)
    return render_template('db_actions.html', message=message)


def backup_database():
    host = 'localhost'
    username = 'root'
    password = ''
    database = 'project'
    backup_file = 'C:/xampp/project_backup.sql'
    command = f'C:/xampp/mysql/bin/mysqldump -h {host} -u {username} --password="{password}" --databases {database} > {backup_file}'
    return subprocess.call(command, shell=True)


def restore_database():
    host = 'localhost'
    username = 'root'
    password = ''
    database = 'project'
    backup_file = 'C:/xampp/project_backup.sql'
    command = f'C:/xampp/mysql/bin/mysql -h {host} -u {username} --password="{password}" {database} < {backup_file}'
    return subprocess.call(command, shell=True)


@app.route('/register_operator/<user_id>')
def register_operator(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE User SET account_status = %s WHERE user_id = %s', ('registered', user_id))
    mysql.connection.commit()
    cursor.close()
    flash('Operator was successfully registered.', 'success')
    return redirect(url_for('operatorslist'))


@app.route('/disable_operator/<user_id>')
def disable_operator(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE User SET account_status = %s, current_reservations = 0, current_borrowings =0'
                   ' WHERE user_id = %s', ('disabled', user_id))
    mysql.connection.commit()
    cursor.close()
    flash('Operator was successfully disabled.', 'success')
    return redirect(url_for('operatorslist'))


@app.route('/delete_operator/<user_id>')
def delete_operator(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM User WHERE user_id = %s', ( user_id,))
    mysql.connection.commit()
    cursor.close()
    flash('Operator was successfully deleted.', 'success')
    return redirect(url_for('operatorslist'))
