-- This file contains the code for the specific queries 3.1.1 - 3.3.2 in sql
-- The fragments of code also exist in the python routes with explanatory comments
-- All  the 'search_variables' are named like that to indicate they will be replaced by the user's input


-- 3.1.1
SELECT SU.school_id, SU.school_name, COUNT(*) AS total_borrows
FROM School_Unit SU
JOIN (
    SELECT user_id, school_id
    FROM User
) U ON SU.school_id = U.school_id
JOIN Borrowing B ON U.user_id = B.user_id
WHERE YEAR(B.starting_date) = 'search_year'
    AND MONTH(B.starting_date) = 'search_month'
GROUP BY SU.school_id, SU.school_name;

-- 3.1.2
SELECT author
FROM book_author
WHERE ISBN IN
(SELECT ISBN FROM book_thematic_category WHERE thematic_category='search_category');

SELECT CONCAT(user.first_name,' ',user.last_name)
AS 'professor'
FROM user
INNER JOIN (SELECT user_id, ISBN, starting_date FROM borrowing) b ON user.user_id = b.user_id
WHERE user_type='professor' AND
ISBN IN (SELECT ISBN FROM book_thematic_category WHERE thematic_category='search_category')
AND YEAR(b.starting_date) = YEAR(CURDATE());

-- 3.1.3
SELECT CONCAT(first_name, ' ', last_name) AS professor, total_borrowings
FROM user
JOIN (
  SELECT MAX(total_borrowings) AS max_borrowings
  FROM user
  WHERE user_type = 'professor'
) m ON user.total_borrowings = m.max_borrowings
WHERE YEAR(date_of_birth) < YEAR(CURDATE()) - 40
  AND user_type = 'professor';

-- 3.1.4
SELECT author
FROM book_author
WHERE ISBN NOT IN(SELECT DISTINCT ISBN FROM borrowing);

-- 3.1.5
SELECT GROUP_CONCAT(CONCAT(user.first_name,' ',user.last_name)) AS operators, result.total_b AS total_borrowings
FROM user
INNER JOIN (
    SELECT u.school_id, COUNT(*) AS total_b
    FROM (
    SELECT school_id, user_id
    FROM User
    ) u
    INNER JOIN (
    SELECT starting_date, user_id
    FROM Borrowing
    ) b ON u.user_id = b.user_id
    WHERE YEAR(b.starting_date) = 'search_year'
    GROUP BY u.school_id
    HAVING COUNT(*) > 20
) AS result ON result.school_id = user.school_id
WHERE user.user_type = 'operator'
GROUP BY result.total_b
HAVING COUNT(*) > 1;

-- 3.1.6
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

-- 3.1.7
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

-- 3.2.1
-- 'search_title', 'search_author','search_category', 'search_copies', 'operator_loggedin_school_id' depend
-- on the operator making the search
SELECT b.title, b.cover_image, b.ISBN,
       (SELECT GROUP_CONCAT(DISTINCT ba.author) FROM Book_author ba WHERE ba.ISBN = b.ISBN) AS authors
FROM Book b
WHERE (b.title = 'search_title' OR 'search_title' IS NULL)
  AND ('search_author' IS NULL OR EXISTS (
    SELECT 1 FROM Book_author ba WHERE ba.ISBN = b.ISBN AND ba.author = 'search_author'
    ))
  AND ('search_category' IS NULL OR EXISTS (
    SELECT 1 FROM Book_thematic_category bt WHERE bt.ISBN = b.ISBN AND bt.thematic_category = 'search_category'
    ))
  AND (b.ISBN IN (SELECT bc.ISBN
                  FROM Belongs_to bc
                  WHERE bc.school_id = 'operator_loggedin_school_id'
                    AND (bc.copies_available = 'search_copies' OR 'search_copies' = '')))
ORDER BY b.title;

-- 3.2.2
SELECT U.user_id, U.username, U.first_name, U.last_name, U.school_id, DATEDIFF(NOW(), B.expected_return) AS days
FROM User U
         INNER JOIN Borrowing B ON U.user_id = B.user_id
WHERE B.borrowing_status = 'late'
  AND (first_name = 'search_first_name' OR 'search_first_name' = '')
  AND (last_name = 'search_last_name' OR 'search_last_name' = '')
  AND (DATEDIFF(NOW(), B.expected_return) = 'search_delay_days' OR 'search_delay_days' = '')
  AND school_id = 'user_loggedin_school_id';

-- 3.2.3
SELECT FORMAT(AVG(r.likert_value), 2) AS average_likert_value
FROM Reviews r
JOIN (SELECT user_id, school_id FROM User) s ON r.user_id = s.user_id
WHERE publication_status = 'published'
  AND (r.user_id = 'search_user_id' OR 'search_user_id' = '')
  AND (r.ISBN IN (SELECT btc.ISBN
                  FROM Book_thematic_category btc
                  WHERE btc.thematic_category = 'search_category') OR 'search_category' = '')
    AND r.user_id IN (SELECT user_id
                    FROM Borrowing)
    AND s.school_id = 'operator_loggenin_school_id'
;

-- 3.3.1
SELECT b.title, b.cover_image, b.ISBN,
       (SELECT GROUP_CONCAT(DISTINCT ba.author) FROM Book_author ba WHERE ba.ISBN = b.ISBN) AS authors
FROM Book b
WHERE (b.title = 'search_title' OR 'search_title' IS NULL)
  AND ('search_author' IS NULL OR EXISTS (
    SELECT 1 FROM Book_author ba WHERE ba.ISBN = b.ISBN AND ba.author = 'search_author'
    ))
  AND ('search_category' IS NULL OR EXISTS (
    SELECT 1 FROM Book_thematic_category bt WHERE bt.ISBN = b.ISBN AND bt.thematic_category = 'search_category'
    ))
  AND (b.ISBN IN (SELECT bc.ISBN
                  FROM Belongs_to bc
                  WHERE bc.school_id = 'operator_loggedin_school_id'));

-- 3.3.2
SELECT ISBN, title
FROM Book
WHERE ISBN IN (SELECT ISBN
               FROM Borrowing
               WHERE user_id = 'user_logged_in_id'); -- index optimizes the subquery method