#### Copying database and table creation here so that my teammates can copy paste in their database



#### database creation

create database corpus_forge;
use corpus_forge;


### table creation

CREATE TABLE uploaded_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_size BIGINT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_text LONGTEXT,
    cleaned_text LONGTEXT,
    word_count INT
);


### print table 
select * from uploaded_files