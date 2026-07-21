-- ============================================================
-- QMaster — Complete Database Setup SQL
-- Run this in phpMyAdmin: http://209.38.120.20/phpmyadmin/
-- Database: db_test
-- ============================================================

-- Alembic version tracking
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- ── Migration 1: questions ──────────────────────────────────
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER NOT NULL AUTO_INCREMENT,
    question TEXT NOT NULL,
    marks DECIMAL(10, 2) NOT NULL DEFAULT 1.00,
    is_global BOOL NOT NULL DEFAULT TRUE,
    is_active BOOL NOT NULL,
    organization_id INTEGER NOT NULL DEFAULT 0,
    user_id INTEGER NOT NULL DEFAULT 0,
    topic_id INTEGER NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX ix_questions_id (id)
);

-- ── Migration 2: question_options ───────────────────────────
CREATE TABLE IF NOT EXISTS question_options (
    id INTEGER NOT NULL AUTO_INCREMENT,
    q_id INTEGER NOT NULL,
    ans TEXT NOT NULL,
    is_correct BOOL NOT NULL,
    PRIMARY KEY (id),
    INDEX ix_question_options_id (id),
    INDEX ix_question_options_q_id (q_id),
    FOREIGN KEY (q_id) REFERENCES questions (id) ON DELETE CASCADE
);

-- ── Migration 3: users ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL AUTO_INCREMENT,
    `role` SMALLINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (email)
);

-- ── Migration 4: organizations ──────────────────────────────
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL UNIQUE,
    is_active BOOL NOT NULL DEFAULT TRUE,
    description TEXT NULL,
    address TEXT NULL,
    phone VARCHAR(50) NULL,
    website VARCHAR(255) NULL,
    PRIMARY KEY (id),
    INDEX ix_organizations_id (id)
);

-- ── Migration 5: organization_users ─────────────────────────
CREATE TABLE IF NOT EXISTS organization_users (
    org_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (org_id, user_id),
    FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- ── Migration 6: topics ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    is_global BOOL NOT NULL DEFAULT TRUE,
    organization_id INTEGER NOT NULL DEFAULT 0,
    user_id INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX ix_topics_id (id)
);

-- ── Migration 7: test_series ────────────────────────────────
CREATE TABLE IF NOT EXISTS test_series (
    id INTEGER NOT NULL AUTO_INCREMENT,
    code VARCHAR(8) NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    access_type ENUM('public', 'invite_only') NOT NULL DEFAULT 'public',
    invite_token_hash VARCHAR(64) NULL,
    org_id INTEGER NOT NULL DEFAULT 0,
    created_by INTEGER NOT NULL,
    valid_until DATETIME NOT NULL,
    duration_seconds INTEGER NOT NULL,
    is_active BOOL NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX ix_test_series_id (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- ── Migration 8: series_questions ───────────────────────────
CREATE TABLE IF NOT EXISTS series_questions (
    series_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (series_id, question_id),
    FOREIGN KEY (series_id) REFERENCES test_series (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

-- ── Migration 9: test_attempts ──────────────────────────────
CREATE TABLE IF NOT EXISTS test_attempts (
    id INTEGER NOT NULL AUTO_INCREMENT,
    series_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status ENUM('in_progress', 'submitted', 'expired') NOT NULL DEFAULT 'in_progress',
    score DECIMAL(10, 2) NOT NULL DEFAULT 0,
    total_marks DECIMAL(10, 2) NOT NULL DEFAULT 0,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    submitted_at DATETIME NULL,
    expires_at DATETIME NULL,
    PRIMARY KEY (id),
    INDEX ix_test_attempts_id (id),
    INDEX ix_test_attempts_series_id (series_id),
    INDEX ix_test_attempts_user_id (user_id),
    FOREIGN KEY (series_id) REFERENCES test_series (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- ── Migration 10: attempt_answers ───────────────────────────
CREATE TABLE IF NOT EXISTS attempt_answers (
    id INTEGER NOT NULL AUTO_INCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_option_id INTEGER NULL,
    is_correct BOOL NULL,
    marks_awarded DECIMAL(10, 2) NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    INDEX ix_attempt_answers_id (id),
    INDEX ix_attempt_answers_attempt_id (attempt_id),
    FOREIGN KEY (attempt_id) REFERENCES test_attempts (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id),
    FOREIGN KEY (selected_option_id) REFERENCES question_options (id)
);

-- ── Alembic version stamp (latest migration) ─────────────────
INSERT IGNORE INTO alembic_version (version_num) VALUES ('f37fce218399');
