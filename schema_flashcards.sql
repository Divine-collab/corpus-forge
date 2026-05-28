-- ─────────────────────────────────────────────────────────────────────────
-- Flashcard Tables for Corpus Forge
-- Run this to initialize flashcard storage capability
-- ─────────────────────────────────────────────────────────────────────────

USE corpus_forge;

-- Flashcard Sets: Stores metadata about generated flashcard sets
CREATE TABLE IF NOT EXISTS flashcard_sets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    set_title VARCHAR(255),
    num_cards INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES uploaded_files(id) ON DELETE CASCADE,
    INDEX idx_document_id (document_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Flashcards: Stores individual flashcard Q&A pairs
CREATE TABLE IF NOT EXISTS flashcards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flashcard_set_id INT NOT NULL,
    front_text TEXT NOT NULL COMMENT 'Question or concept (front side)',
    back_text TEXT NOT NULL COMMENT 'Answer or explanation (back side)',
    card_order INT COMMENT 'Order within the set (1-based)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flashcard_set_id) REFERENCES flashcard_sets(id) ON DELETE CASCADE,
    INDEX idx_set_id (flashcard_set_id),
    INDEX idx_card_order (card_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verify tables exist
SHOW TABLES LIKE 'flashcard%';
