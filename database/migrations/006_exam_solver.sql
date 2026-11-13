USE taskforge;
CREATE TABLE IF NOT EXISTS exam_runs (
 id BIGINT AUTO_INCREMENT PRIMARY KEY,
 user_id BIGINT NOT NULL,
 filename VARCHAR(255) NOT NULL,
 storage_path VARCHAR(500) NOT NULL,
 extracted_text LONGTEXT NOT NULL,
 result_json JSON NOT NULL,
 status VARCHAR(24) NOT NULL DEFAULT 'extracted',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_exam_run_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
 INDEX idx_exam_user_created (user_id, created_at)
) ENGINE=InnoDB;
