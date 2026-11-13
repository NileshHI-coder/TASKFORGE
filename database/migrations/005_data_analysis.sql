USE taskforge;
CREATE TABLE IF NOT EXISTS data_analysis_runs (
 id BIGINT AUTO_INCREMENT PRIMARY KEY,
 user_id BIGINT NOT NULL,
 filename VARCHAR(255) NOT NULL,
 storage_path VARCHAR(500) NOT NULL,
 row_count INT NOT NULL DEFAULT 0,
 column_count INT NOT NULL DEFAULT 0,
 result_json JSON NOT NULL,
 ai_insights LONGTEXT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_analysis_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
 INDEX idx_analysis_user_created (user_id, created_at)
) ENGINE=InnoDB;
