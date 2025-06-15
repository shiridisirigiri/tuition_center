drop table if exists students;
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    fees INTEGER NOT NULL
);
DROP TABLE IF EXISTS courses;

CREATE TABLE courses (
    course_id int PRIMARY KEY,
    course_name TEXT NOT NULL,
    fees INTEGER NOT NULL,
    faculty_name TEXT NOT NULL,
    datetime_value TEXT NOT NULL,
    duration TEXT NOT NULL
);
