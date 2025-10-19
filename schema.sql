PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS authors (
  id     INTEGER PRIMARY KEY,
  name   TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS books (
  id           INTEGER PRIMARY KEY,
  title        TEXT NOT NULL,
  author_id    INTEGER REFERENCES authors(id) ON DELETE SET NULL,
  pages        INTEGER,
  year         INTEGER,
  status       TEXT NOT NULL DEFAULT 'to_read',
  notes        TEXT,
  started_on   TEXT,
  finished_on  TEXT,
  created_at   TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tags (
  id    INTEGER PRIMARY KEY,
  name  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS book_tags (
  book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  tag_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (book_id, tag_id)
);

CREATE TABLE IF NOT EXISTS reading_logs (
  id         INTEGER PRIMARY KEY,
  book_id    INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  date       TEXT NOT NULL,
  pages_read INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
