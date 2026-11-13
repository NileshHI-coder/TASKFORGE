USE taskforge;

-- Run this migration only if TaskForge was installed using the Milestone 1 schema.
ALTER TABLE tasks
  ADD COLUMN plan_approved BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE subtasks
  ADD COLUMN expected_output TEXT NULL,
  ADD COLUMN dependencies JSON NULL;
