SET GLOBAL event_scheduler=ON;

CREATE TABLE IF NOT EXISTS School_Unit
(
    school_id INT UNSIGNED NOT NULL AUTO_INCREMENT, /*for example 0031*/
    school_name VARCHAR(170) NOT NULL,
    address VARCHAR(200) NOT NULL,
    city VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    d_first_name VARCHAR(50) NOT NULL, /*d_ at the beginning is for director*/
    d_last_name VARCHAR(50) NOT NULL,
    o_first_name VARCHAR(50) NOT NULL, /*o_ at the beginning is for (library) operator*/
    o_last_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (school_id)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS School_Unit_phone_number
(
    phone_number CHAR(10) NOT NULL, /*for example 2109827923*/
    school_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (phone_number, school_id),
    CONSTRAINT fk_school_phone FOREIGN KEY (school_id) REFERENCES School_unit (school_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT valid_phone_number CHECK (phone_number RLIKE ('[0-9]{10}')) -- checks that all characters are digits
) ENGINE = InnoDB;

CREATE TABLE if NOT EXISTS Book
(
    ISBN CHAR(13) NOT NULL,
    title VARCHAR(255) NOT NULL,
    publisher VARCHAR(60) NOT NULL,
    page_number INT UNSIGNED NOT NULL,
    summary VARCHAR(1000) NOT NULL,
    cover_image VARCHAR(255) NOT NULL,
    language VARCHAR(50) NOT NULL,
    PRIMARY KEY (ISBN)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS Book_author
(
    author VARCHAR(110) NOT NULL,
    ISBN CHAR(13) NOT NULL,
    PRIMARY KEY (author, ISBN),
    CONSTRAINT fk_book_author FOREIGN KEY (ISBN) REFERENCES Book (ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS Book_thematic_category
(
    thematic_category VARCHAR(50) NOT NULL,
    ISBN CHAR(13) NOT NULL,
    PRIMARY KEY (thematic_category, ISBN),
    CONSTRAINT fk_book_thematic_category FOREIGN KEY (ISBN) REFERENCES Book (ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS Book_keyword
(
    keyword VARCHAR(50) NOT NULL,
    ISBN CHAR(13) NOT NULL,
    PRIMARY KEY (keyword, ISBN),
    CONSTRAINT fk_book_keyword FOREIGN KEY (ISBN) REFERENCES Book (ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS Belongs_to
(
  school_id INT UNSIGNED NOT NULL,           /*school ID*/
  ISBN varchar(20) NOT NULL,                   /*ISBN*/
  copies_available INT UNSIGNED NOT NULL,
  PRIMARY KEY (school_id, ISBN),
  CONSTRAINT fk_belongs_to_school FOREIGN KEY (school_id) REFERENCES School_Unit (school_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
  CONSTRAINT fk_book_belongs_to FOREIGN KEY (ISBN) REFERENCES Book (ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS User
(
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT, /*for example 003120046*/
    school_id  INT UNSIGNED NOT NULL,
    username VARCHAR(30)  NOT NULL,
    password VARCHAR(20)  NOT NULL,
    user_type ENUM ('student', 'professor', 'operator') NOT NULL,
    email VARCHAR(256) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    account_status ENUM ('pending', 'registered', 'disabled') DEFAULT 'pending' ,
    current_reservations INT UNSIGNED DEFAULT 0 NOT NULL,
    current_borrowings INT UNSIGNED DEFAULT 0 NOT NULL,
    total_borrowings INT UNSIGNED DEFAULT 0 NOT NULL,
    total_reservations INT UNSIGNED DEFAULT 0 NOT NULL,
    PRIMARY KEY (user_id),
    CONSTRAINT fk_member_of FOREIGN KEY (school_id) REFERENCES School_Unit (school_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT limits_per_week CHECK((user_type='student' AND current_borrowings<=2 AND current_reservations<=2)
                                     OR (user_type='professor' AND current_borrowings<=1 AND current_reservations<=1)
                                     OR user_type='operator')
)ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS Administrator
(
    admin_username VARCHAR(30) NOT NULL,
    admin_password VARCHAR(20) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(256) NOT NULL,
    PRIMARY KEY (admin_username)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS Reservation
(   reservation_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ISBN CHAR(13) NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    date_made DATE NOT NULL,
    reservation_status ENUM ('made','on hold','cancelled','served') DEFAULT 'made' NOT NULL,
    PRIMARY KEY (reservation_id),
    CONSTRAINT fk_reserves_book FOREIGN KEY (ISBN) REFERENCES Book (ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_user_reserves FOREIGN KEY (user_id) REFERENCES USER (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE

) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS Borrowing
(
    borrowing_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    reservation_id INT UNSIGNED DEFAULT NULL,
    ISBN CHAR(13) NOT NULL,
    starting_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    expected_return DATE,
    borrowing_status ENUM ('active', 'late', 'completed', 'completed late') DEFAULT 'active' NOT NULL,
    PRIMARY KEY (borrowing_id),
    CONSTRAINT fk_borrows_book FOREIGN KEY (ISBN) REFERENCES Book (ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_user_borrows FOREIGN KEY (user_id) REFERENCES USER (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_borrows_reservation FOREIGN KEY (reservation_id) REFERENCES Reservation (reservation_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS Reviews
(
    ISBN CHAR(13) NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    free_text TEXT NOT NULL,
    likert_value INT CHECK (likert_value >= 0 AND likert_value <= 5),
    publication_status ENUM ('written', 'published', 'declined') NOT NULL DEFAULT 'written',
    PRIMARY KEY (ISBN, user_id),
    CONSTRAINT fk_reviews_book FOREIGN KEY (ISBN) REFERENCES Book (ISBN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_user_reviews FOREIGN KEY (user_id) REFERENCES USER (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE INDEX idx_borrowing_info ON Borrowing (user_id, ISBN, starting_date);
CREATE INDEX idx_book_info ON Book (title, cover_image);

DELIMITER //
CREATE TRIGGER IF NOT EXISTS check_user_age BEFORE INSERT ON User
FOR EACH ROW
BEGIN
    DECLARE age INT;
    SET age= TIMESTAMPDIFF(YEAR,NEW.date_of_birth,CURDATE());

    IF NEW.user_type = 'student' THEN
        IF age<6 OR age>18 THEN
            SET @error_message = CONCAT('Invalid age for student with ID', NEW.user_id, '. Age must be between 6 and 18., but it is', CAST(age AS CHAR));
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @error_message;
        END IF;
    ELSEIF NEW.user_type IN ('professor', 'operator') THEN
        IF age<22 THEN
            SET @error_message = CONCAT('Invalid age for ', NEW.user_type, ' with ID ', CAST(NEW.user_id AS CHAR), '. Age must be above 22, but it is ', CAST(age AS CHAR));
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @error_message;
        END IF;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER IF NOT EXISTS pending_user_details BEFORE INSERT ON User
FOR EACH ROW
BEGIN
    IF NEW.account_status = 'pending' THEN
        SET NEW.current_reservations=0, NEW.current_borrowings=0, NEW.total_borrowings=0;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER IF NOT EXISTS disabled_user_updates AFTER UPDATE ON User
FOR EACH ROW
BEGIN
    IF NEW.account_status = 'disabled' AND OLD.account_status <> 'disabled' THEN
        UPDATE Reservation
        SET reservation_status = 'cancelled'
        WHERE user_id = NEW.user_id
        AND reservation_status IN ('made', 'on hold');

        UPDATE Borrowing
        SET borrowing_status = 'completed'
        WHERE user_id = NEW.user_id
        AND borrowing_status IN ('active', 'late');
    END IF;
END;
DELIMITER ;


-- triggers for Borrowing
DELIMITER //
CREATE TRIGGER IF NOT EXISTS before_borrowing_insert BEFORE INSERT ON Borrowing
FOR EACH ROW
BEGIN
    DECLARE user_status VARCHAR(10);
    DECLARE school INT;
    SELECT account_status INTO user_status FROM User WHERE user_id = NEW.user_id;
    IF user_status = 'pending' OR user_status = 'disabled' AND NEW.return_date IS NULL THEN
        SET @error_message = CONCAT('Cannot make a borrowing due to account status.', NEW.user_id, user_status);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @error_message;
    END IF;

    IF NEW.starting_date > CURDATE() OR NEW.return_date < NEW.starting_date THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid borrowing dates.';
    END IF;

    SET NEW.expected_return = NEW.starting_date + INTERVAL 7 DAY;

    SET NEW.borrowing_status = CASE
        WHEN NEW.return_date IS NULL THEN
            IF(CURDATE() < NEW.expected_return, 'active', 'late')
        WHEN NEW.return_date > NEW.expected_return THEN 'completed late'
        ELSE 'completed'
        END;

    IF NEW.return_date IS NULL THEN
        SELECT school_id INTO school FROM User WHERE user_id = NEW.user_id;
        UPDATE Belongs_to
        SET copies_available = copies_available - 1
        WHERE school_id = school AND ISBN = NEW.ISBN;
    END IF;

    IF NEW.return_date IS NULL THEN
        UPDATE User
        SET current_borrowings = current_borrowings + 1, total_borrowings = total_borrowings + 1
        WHERE user_id = NEW.user_id;
    ELSE
        UPDATE User
        SET total_borrowings = total_borrowings + 1
        WHERE user_id = NEW.user_id;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER IF NOT EXISTS updates_after_borrowing_return
AFTER UPDATE ON Borrowing
FOR EACH ROW
BEGIN
    -- Decrease current_borrowings by 1 for completed or completed late borrowings
    IF NEW.borrowing_status IN ('completed', 'completed late') AND OLD.borrowing_status NOT IN ('completed', 'completed late') THEN
        UPDATE User
        SET current_borrowings = current_borrowings - 1
        WHERE user_id = NEW.user_id;

        UPDATE Belongs_to
        SET copies_available = copies_available + 1
        WHERE school_id = (SELECT school_id FROM User WHERE user_id = NEW.user_id) AND ISBN = NEW.ISBN;
    END IF;

END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER IF NOT EXISTS updates_after_borrowing_delete
AFTER DELETE ON Borrowing
FOR EACH ROW
BEGIN
    -- Decrease current_borrowings by 1 for deleted active borrowings
    IF OLD.borrowing_status = 'active' THEN
        UPDATE User
        SET current_borrowings = current_borrowings - 1
        WHERE user_id = OLD.user_id;
    END IF;
       -- Decrease total_borrowings by 1 for deleted borrowings
    UPDATE User
    SET total_borrowings = total_borrowings - 1
    WHERE user_id = OLD.user_id;

    UPDATE Belongs_to
    SET copies_available = copies_available + 1
    WHERE school_id = (SELECT school_id FROM User WHERE user_id = OLD.user_id) AND ISBN = OLD.ISBN;

END //
DELIMITER ;


-- triggers for reservation
DELIMITER //
CREATE TRIGGER IF NOT EXISTS check_reservation_details BEFORE INSERT ON reservation
FOR EACH ROW
BEGIN
    IF NEW.date_made > CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid reservation date.';
    END IF;

    IF DATEDIFF(NEW.date_made, CURDATE()) >= 7 THEN
        SET NEW.reservation_status='cancelled';
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER IF NOT EXISTS valid_user_reserving BEFORE INSERT ON Reservation
FOR EACH ROW
BEGIN
    DECLARE user_status VARCHAR(10);
    SELECT account_status INTO user_status FROM User WHERE user_id = NEW.user_id;
    SET @error_message = CONCAT('Cannot make a reservation due to account status:', user_status, '.');

    IF user_status = 'pending' OR user_status = 'disabled' AND NEW.reservation_status NOT IN ('cancelled', 'served') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @error_message;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER IF NOT EXISTS on_hold_reservation
BEFORE INSERT ON Reservation
FOR EACH ROW
BEGIN
    -- Get school_id from User table
    DECLARE school, copies INT;
    SELECT school_id INTO school FROM User WHERE user_id = NEW.user_id;

    -- Check if copies_available is 0 for the given school_id and ISBN
    SELECT copies_available INTO copies FROM Belongs_to WHERE school_id = school AND ISBN = NEW.ISBN;

    -- Set reservation status to 'on hold' if copies_available is 0
    IF copies = 0 THEN
        SET NEW.reservation_status = 'on hold';
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER IF NOT EXISTS increase_current_reservations
AFTER INSERT ON Reservation
FOR EACH ROW
BEGIN
    -- Increase current_reservations by 1 for new reservations
    IF NEW.reservation_status IN ('made', 'on hold') THEN
        UPDATE User
        SET current_reservations = current_reservations + 1, total_reservations = total_reservations + 1
        WHERE user_id = NEW.user_id;
    ELSE
        UPDATE User
        SET total_reservations = total_reservations + 1
        WHERE user_id = NEW.user_id;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER if not exists borrow_after_serving_reservation
AFTER UPDATE ON Reservation
FOR EACH ROW
BEGIN
IF (OLD.reservation_status IN ('on hold', 'made') AND NEW.reservation_status = 'served')
THEN
  INSERT INTO Borrowing (reservation_id, user_id, ISBN, starting_date, expected_return)
  VALUES (NEW.reservation_id, NEW.user_id, NEW.ISBN, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY));
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER IF NOT EXISTS decrease_current_reservations
AFTER UPDATE ON Reservation
FOR EACH ROW
BEGIN
    -- Decrease current_reservations by 1 for canceled or served reservations
    IF NEW.reservation_status IN ('cancelled', 'served') AND OLD.reservation_status NOT IN ('cancelled', 'served') THEN
        UPDATE User
        SET current_reservations = current_reservations - 1
        WHERE user_id = NEW.user_id;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER IF NOT EXISTS decrease_reservations_after_delete
BEFORE DELETE ON Reservation
FOR EACH ROW
BEGIN
        -- Decrease current_reservations by 1 for deleted active reservations
    IF OLD.reservation_status IN ('made', 'on hold') THEN
        UPDATE User
        SET current_reservations = current_reservations - 1
        WHERE user_id = OLD.user_id;
    END IF;

       -- Decrease total_reservations by 1 for deleted reservations
    UPDATE User
    SET total_reservations = total_reservations - 1
    WHERE user_id = OLD.user_id;


END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER if not exists update_to_on_hold_reservations
BEFORE UPDATE ON Belongs_to
FOR EACH ROW
BEGIN
    IF NEW.copies_available = 0 AND OLD.copies_available > 0 THEN
        UPDATE Reservation
        SET reservation_status = 'on hold'
        WHERE ISBN = NEW.ISBN AND reservation_status='made';
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER if not exists update_to_made_reservations
BEFORE UPDATE ON Belongs_to
FOR EACH ROW
BEGIN
    IF NEW.copies_available > 0 AND OLD.copies_available = 0 THEN
        UPDATE Reservation
        SET reservation_status = 'made'
        WHERE ISBN = NEW.ISBN AND reservation_status='on hold';
    END IF;
END //
DELIMITER ;

-- event for time dependent changes
DELIMITER //
CREATE EVENT IF NOT EXISTS status_updates_with_time
ON SCHEDULE EVERY 12 HOUR
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    UPDATE Reservation
    SET reservation_status = 'cancelled'
    WHERE reservation_status IN ('made', 'on hold') AND DATE_ADD(date_made, INTERVAL 6 DAY) <= CURDATE();

    UPDATE Borrowing
    SET borrowing_status = 'late'
    WHERE borrowing_status ='active' AND return_date IS NULL AND expected_return < CURDATE();
    END //
DELIMITER ;

-- triggers for Reviews
DELIMITER //
CREATE TRIGGER IF NOT EXISTS valid_user_reviewing BEFORE INSERT ON Reviews
FOR EACH ROW
BEGIN
    DECLARE user_status VARCHAR(10);
    SELECT account_status INTO user_status FROM User WHERE user_id = NEW.user_id;
    SET @error_message = CONCAT('Cannot make a reservation due to account status: ', user_status, '.', 'ID is ', NEW.user_id);

    IF user_status = 'pending' OR user_status = 'disabled' AND NEW.publication_status IN ('written') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @error_message;
    END IF;
END //
DELIMITER ;
