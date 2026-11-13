CREATE DATABASE IF NOT EXISTS taskforge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE taskforge;

CREATE TABLE IF NOT EXISTS users (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120) NOT NULL,
 email VARCHAR(255) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tasks (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, user_id BIGINT NOT NULL,
 title VARCHAR(255) NOT NULL, description TEXT NULL, category VARCHAR(50) NOT NULL DEFAULT 'general',
 status ENUM('pending','planning','running','verification','completed','failed','cancelled') NOT NULL DEFAULT 'pending',
 plan_approved BOOLEAN NOT NULL DEFAULT FALSE, result LONGTEXT NULL, error_message TEXT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 CONSTRAINT fk_tasks_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
 INDEX idx_tasks_user_created (user_id, created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subtasks (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, task_id BIGINT NOT NULL,
 title VARCHAR(255) NOT NULL, description TEXT NULL, agent_type VARCHAR(80) NOT NULL,
 status ENUM('queued','running','waiting_for_approval','completed','failed','skipped') NOT NULL DEFAULT 'queued',
 expected_output TEXT NULL, dependencies JSON NULL, output LONGTEXT NULL, retry_count INT NOT NULL DEFAULT 0, started_at DATETIME NULL, completed_at DATETIME NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_subtasks_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE, INDEX idx_subtasks_task (task_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS agent_executions (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, task_id BIGINT NOT NULL, subtask_id BIGINT NULL,
 agent_name VARCHAR(100) NOT NULL, status VARCHAR(40) NOT NULL, input_summary TEXT NULL, output_summary TEXT NULL,
 error_summary TEXT NULL, started_at DATETIME NULL, completed_at DATETIME NULL,
 CONSTRAINT fk_exec_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
 CONSTRAINT fk_exec_subtask FOREIGN KEY (subtask_id) REFERENCES subtasks(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS uploaded_files (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, user_id BIGINT NOT NULL, task_id BIGINT NULL,
 original_name VARCHAR(255) NOT NULL, stored_name VARCHAR(255) NOT NULL, mime_type VARCHAR(120) NOT NULL,
 size_bytes BIGINT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_upload_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
 CONSTRAINT fk_upload_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS generated_files (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, task_id BIGINT NOT NULL,
 filename VARCHAR(255) NOT NULL, storage_path VARCHAR(500) NOT NULL, mime_type VARCHAR(120) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_generated_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS task_results (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, task_id BIGINT NOT NULL,
 result_type VARCHAR(80) NOT NULL, content LONGTEXT NOT NULL, verification_status VARCHAR(40) NOT NULL DEFAULT 'needs_review',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_results_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS exam_questions (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, task_id BIGINT NOT NULL, question_number VARCHAR(30) NOT NULL,
 page_number INT NULL, question_text LONGTEXT NOT NULL, question_type VARCHAR(50) NULL, subject VARCHAR(120) NULL,
 topic VARCHAR(120) NULL, extraction_status VARCHAR(40) NOT NULL DEFAULT 'needs_review',
 CONSTRAINT fk_exam_question_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS exam_solutions (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, question_id BIGINT NOT NULL, answer LONGTEXT NULL, explanation LONGTEXT NULL,
 verification_status ENUM('verified','partially_verified','needs_review','unable_to_solve') NOT NULL DEFAULT 'needs_review',
 verifier_notes TEXT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_solution_question FOREIGN KEY (question_id) REFERENCES exam_questions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS activity_logs (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, user_id BIGINT NULL, task_id BIGINT NULL,
 event_type VARCHAR(100) NOT NULL, message TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_activity_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
 CONSTRAINT fk_activity_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE, INDEX idx_activity_task (task_id)
) ENGINE=InnoDB;

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
