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
select * from uploaded_files;


CREATE TABLE api_usage_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    query_text LONGTEXT,
    input_tokens INT,
    output_tokens INT,
    total_tokens INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES uploaded_files(id) ON DELETE CASCADE
);

### print api usage logs
select * from api_usage_logs;