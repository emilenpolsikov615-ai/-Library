"""База данных библиотеки: пользователи, книги, отзывы (SQLite)."""
import hashlib
import hmac
import os
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    salt BLOB NOT NULL,
    pw_hash BLOB NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
);
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    description TEXT NOT NULL,
    body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL REFERENCES books(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT NOT NULL DEFAULT '',
    created TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (book_id, user_id)
);
"""

ADMIN_USERNAME = "emilenpolsikov615@gmail.com"

PLACEHOLDER = (
    "Здесь будет полный текст книги.\n\n"
    "Чтобы добавить настоящий текст, создайте файл books/{id}.txt "
    "(кодировка UTF-8) рядом с main.py. Абзацы разделяйте пустой строкой. "
    "При следующем запуске приложение подхватит его автоматически."
)

# (название, автор, жанр, описание)
SEED_BOOKS = [
    ("Война и мир", "Л. Толстой", "Классика",
     "Роман-эпопея о русском обществе в эпоху наполеоновских войн."),
    ("Преступление и наказание", "Ф. Достоевский", "Классика",
     "История студента Раскольникова."),
    ("Мастер и Маргарита", "М. Булгаков", "Фантастика",
     "Дьявол приезжает в Москву 1930-х."),
    ("Пикник на обочине", "А. и Б. Стругацкие", "Фантастика",
     "Сталкер идёт в Зону."),
]

_ITERATIONS = 100_000

BOOK_SELECT = """
SELECT b.*, AVG(r.rating) AS avg_rating, COUNT(r.id) AS reviews_count
FROM books b LEFT JOIN reviews r ON r.book_id = b.id
"""


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)


class Database:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self._migrate()
        self._seed()
        self._ensure_admin()

    def _migrate(self):
        cols = [r["name"] for r in self.conn.execute("PRAGMA table_info(users)")]
        if "role" not in cols:
            self.conn.execute(
                "ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"
            )
            self.conn.commit()

    def _ensure_admin(self):
        self.conn.execute(
            "UPDATE users SET role = 'admin' WHERE username = ?",
            (ADMIN_USERNAME,),
        )
        self.conn.commit()

    def _seed(self):
        if self.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
            for title, author, genre, desc in SEED_BOOKS:
                self.conn.execute(
                    "INSERT INTO books(title, author, genre, description, body) "
                    "VALUES (?,?,?,?,?)",
                    (title, author, genre, desc, ""),
                )
            self.conn.commit()

    def import_texts(self, folder):
        """Подхватывает файлы books/<id>.txt как текст книги."""
        if not os.path.isdir(folder):
            return
        for row in self.conn.execute("SELECT id FROM books").fetchall():
            path = os.path.join(folder, "%d.txt" % row["id"])
            if os.path.isfile(path):
                with open(path, encoding="utf-8") as f:
                    self.conn.execute(
                        "UPDATE books SET body = ? WHERE id = ?", (f.read(), row["id"])
                    )
        self.conn.commit()

    # ---------- пользователи ----------
    def register(self, username, password):
        """Возвращает (user, сообщение). user = None при ошибке."""
        username = username.strip()
        if len(username) < 3:
            return None, "Логин: минимум 3 символа"
        if len(password) < 4:
            return None, "Пароль: минимум 4 символа"
        salt = os.urandom(16)
        try:
            cur = self.conn.execute(
                "INSERT INTO users(username, salt, pw_hash) VALUES (?,?,?)",
                (username, salt, _hash(password, salt)),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            return None, "Такой логин уже занят"
        self._ensure_admin()
        role = "admin" if username.lower() == ADMIN_USERNAME.lower() else "user"
        return {"id": cur.lastrowid, "username": username, "role": role}, ""

    def login(self, username, password):
        self._ensure_admin()
        row = self.conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()
        if row is None:
            return None
        if hmac.compare_digest(row["pw_hash"], _hash(password, row["salt"])):
            return {"id": row["id"], "username": row["username"], "role": row["role"]}
        return None

    # ---------- книги ----------
    def genres(self):
        rows = self.conn.execute(
            "SELECT DISTINCT genre FROM books ORDER BY genre"
        ).fetchall()
        return [r["genre"] for r in rows]

    def books(self, genre=None):
        if genre and genre != "Все":
            return self.conn.execute(
                BOOK_SELECT + " WHERE b.genre = ? GROUP BY b.id ORDER BY b.title",
                (genre,),
            ).fetchall()
        return self.conn.execute(
            BOOK_SELECT + " GROUP BY b.id ORDER BY b.title"
        ).fetchall()

    def book(self, book_id):
        return self.conn.execute(
            BOOK_SELECT + " WHERE b.id = ? GROUP BY b.id", (book_id,)
        ).fetchone()

    def book_text(self, book_id):
        row = self.conn.execute(
            "SELECT body FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        body = row["body"] if row else ""
        return body if body.strip() else PLACEHOLDER

    # ---------- отзывы ----------
    def reviews(self, book_id):
        return self.conn.execute(
            "SELECT r.*, u.username FROM reviews r JOIN users u ON u.id = r.user_id "
            "WHERE r.book_id = ? ORDER BY r.id DESC",
            (book_id,),
        ).fetchall()

    def my_review(self, book_id, user_id):
        return self.conn.execute(
            "SELECT * FROM reviews WHERE book_id = ? AND user_id = ?",
            (book_id, user_id),
        ).fetchone()

    def user_reviews(self, user_id):
        return self.conn.execute(
            "SELECT r.*, b.title FROM reviews r JOIN books b ON b.id = r.book_id "
            "WHERE r.user_id = ? ORDER BY r.id DESC",
            (user_id,),
        ).fetchall()

    def save_review(self, book_id, user_id, rating, comment):
        """Один отзыв на книгу от пользователя: повторное сохранение обновляет его."""
        rating = max(1, min(5, int(rating)))
        self.conn.execute(
            "INSERT INTO reviews(book_id, user_id, rating, comment) VALUES (?,?,?,?) "
            "ON CONFLICT(book_id, user_id) DO UPDATE SET "
            "rating = excluded.rating, comment = excluded.comment, created = date('now')",
            (book_id, user_id, rating, comment.strip()[:1000]),
        )
        self.conn.commit()

    # ---------- администрирование ----------
    def users(self):
        return self.conn.execute(
            "SELECT u.id, u.username, u.role, COUNT(r.id) AS reviews_count "
            "FROM users u LEFT JOIN reviews r ON r.user_id = u.id "
            "GROUP BY u.id ORDER BY u.id"
        ).fetchall()

    def delete_user(self, user_id):
        self.conn.execute("DELETE FROM reviews WHERE user_id = ?", (user_id,))
        self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()