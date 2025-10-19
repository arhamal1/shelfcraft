from flask import Flask, request, redirect, render_template, url_for, abort
from db import get_conn, init_db
import os

app = Flask(__name__)

@app.get("/")
def home():
    with get_conn() as conn:
        c = conn.execute("SELECT COUNT(*) AS c FROM books").fetchone()["c"]
    return f'ShelfCraft. Books tracked: {c} <br><a href="/books">View list</a>'

@app.get("/add")
def add_page():
    return render_template("add.html")

@app.post("/add")
def add_book():
    title = request.form.get("title")
    pages = request.form.get("pages", type=int)
    status = request.form.get("status", "to_read")
    if not title:
        return "Title required", 400
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO books (title, pages, status) VALUES (?, ?, ?)",
            (title, pages, status)
        )
        conn.commit()
    return redirect("/")

@app.get("/books")
def list_books():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, title, pages, status FROM books ORDER BY id DESC"
        ).fetchall()
    return render_template("list.html", books=rows)

@app.get("/edit/<int:book_id>")
def edit_page(book_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, title, pages, status FROM books WHERE id = ?", (book_id,)
        ).fetchone()
    if not row:
        abort(404)
    return render_template("edit.html", b=row)

@app.post("/edit/<int:book_id>")
def edit_book(book_id: int):
    title = request.form.get("title")
    pages = request.form.get("pages", type=int)
    status = request.form.get("status", "to_read")
    if not title:
        return "Title required", 400
    with get_conn() as conn:
        conn.execute(
            "UPDATE books SET title = ?, pages = ?, status = ?, updated_at = datetime('now') WHERE id = ?",
            (title, pages, status, book_id),
        )
        conn.commit()
    return redirect(url_for("list_books"))

@app.post("/delete/<int:book_id>")
def delete_book(book_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
    return redirect(url_for("list_books"))

@app.get("/book/<int:book_id>")
def book_detail(book_id: int):
    with get_conn() as conn:
        book = conn.execute(
            "SELECT id, title, pages, status FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        if not book:
            abort(404)
        logs = conn.execute(
            "SELECT id, date, pages_read FROM reading_logs WHERE book_id = ? ORDER BY date DESC",
            (book_id,),
        ).fetchall()
        total_logged = sum(r["pages_read"] for r in logs)
    return render_template("book.html", b=book, logs=logs, total_logged=total_logged)

@app.post("/book/<int:book_id>/log")
def add_log(book_id: int):
    pages_read = request.form.get("pages_read", type=int)
    date = request.form.get("date") or None
    if not pages_read or pages_read < 1:
        return "pages_read must be positive", 400
    with get_conn() as conn:
        if date:
            conn.execute(
                "INSERT INTO reading_logs (book_id, date, pages_read) VALUES (?, ?, ?)",
                (book_id, date, pages_read),
            )
        else:
            conn.execute(
                "INSERT INTO reading_logs (book_id, date, pages_read) VALUES (?, date('now'), ?)",
                (book_id, pages_read),
            )
        conn.commit()
    return redirect(url_for("book_detail", book_id=book_id))

@app.get("/analytics")
def analytics():
    with get_conn() as conn:
        totals = conn.execute("""
            SELECT
              (SELECT COUNT(*) FROM books) AS books_count,
              (SELECT COUNT(*) FROM books WHERE status = 'reading') AS reading_count,
              (SELECT COUNT(*) FROM books WHERE status = 'read') AS read_count,
              (SELECT COALESCE(SUM(pages),0) FROM books) AS pages_total
        """).fetchone()
        pages_read_logged = conn.execute(
            "SELECT COALESCE(SUM(pages_read),0) AS s FROM reading_logs"
        ).fetchone()["s"]
        per_day = conn.execute("""
            SELECT date, SUM(pages_read) AS pages
            FROM reading_logs
            GROUP BY date
            ORDER BY date DESC
            LIMIT 14
        """).fetchall()
    return render_template(
        "analytics.html",
        totals=totals,
        pages_read_logged=pages_read_logged,
        per_day=per_day,
    )

if __name__ == "__main__":
    try:
        init_db()
    except Exception:
        pass
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))