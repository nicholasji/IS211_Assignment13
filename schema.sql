drop table if exists student;
CREATE TABLE student (id INTEGER PRIMARY KEY ASC,
                first_name TEXT,
                last_name TEXT);

drop table if exists quiz;
CREATE TABLE quiz (id INTEGER PRIMARY KEY ASC,
		subject TEXT,
                num_questions INTEGER,
                date DATE);

drop table if exists results;
CREATE TABLE results (score INTEGER,
                      quiz_id INTEGER,
                      student_id INTEGER,
                      FOREIGN KEY (quiz_id) REFERENCES quiz(id),
                      FOREIGN KEY (student_id) REFERENCES student(id));

