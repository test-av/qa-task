"""Product Management - CRUD demo (Flask + SQLite)."""

import sqlite3
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "products.db")

app = Flask(__name__, static_folder="static")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            details TEXT,
            price REAL,
            quantity INTEGER,
            created_at TEXT
        )
        """
    )
    cur = conn.execute("SELECT COUNT(*) AS c FROM products")
    if cur.fetchone()["c"] == 0:
        sample = [
            (1, "Brake pads", "Brakes", "Front ceramic brake pads", 45.99, 30, "2026-06-10 09:15:00"),
            (2, "Oil filter", "Filters", "Spin-on oil filter", 8.50, 120, "2026-06-11 14:30:00"),
            (3, "Spark plug", "Engine", "Iridium spark plug", 12.99, 80, "2026-06-12 08:05:00"),
            (4, "Shock absorber", "Suspension", "Front gas shock absorber", 64.00, 18, "2026-06-13 16:45:00"),
            (5, "Alternator", "Electrical", "12V 120A alternator", 189.00, 6, "2026-06-14 10:20:00"),
            (6, "Side mirror", "Body", "Left heated wing mirror", 75.50, 10, "2026-06-14 15:50:00"),
        ]
        conn.executemany(
            "INSERT INTO products (id, name, category, details, price, quantity, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            sample,
        )
    conn.commit()
    conn.close()


def row_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "details": row["details"],
        "price": row["price"],
        "quantity": row["quantity"],
        "created_at": row["created_at"],
    }


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


USERS = {
    "admin": "admin123",
}


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    password = data.get("password")


    if username not in USERS:
        return jsonify({"error": "User not found"}), 401
    if USERS[username] != password:
        return jsonify({"error": "Wrong password"}), 401

    return jsonify({"status": "ok", "token": "demo-token-" + username}), 200


@app.route("/api/products", methods=["GET"])
def list_products():
    search = request.args.get("search", "")
    conn = get_db()
    if search:
        rows = conn.execute(
            "SELECT * FROM products WHERE name GLOB ?", ("*" + search + "*",)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/products/<int:pid>", methods=["GET"])
def get_product(pid):
    conn = get_db()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(row_to_dict(row))


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json(force=True, silent=True) or {}
    pid = data.get("id")
    name = data.get("name")
    category = data.get("category")
    details = data.get("details")
    price = data.get("price")
    quantity = data.get("quantity")

    if pid is None or (isinstance(pid, str) and pid.strip() == ""):
        return jsonify({"error": "ID is required"}), 400

    if price is None or (isinstance(price, str) and price.strip() == ""):
        return jsonify({"error": "Price is required"}), 400

    conn = get_db()
    exists = conn.execute("SELECT 1 FROM products WHERE id = ?", (pid,)).fetchone()
    if exists is not None:
        conn.close()
        return jsonify({"error": "A product with this ID already exists"}), 409

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute(
            "INSERT INTO products (id, name, category, details, price, quantity, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (pid, name, category, details, price, quantity, created_at),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "A product with this ID already exists"}), 409
    row = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(row)), 201


@app.route("/api/products/<int:pid>", methods=["PUT"])
def update_product(pid):
    data = request.get_json(force=True, silent=True) or {}
    conn = get_db()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
    if row is None:
        conn.close()
        return jsonify({"error": "Not found"}), 404

    new_id = data.get("id", row["id"])
    name = data.get("name", row["name"])
    details = data.get("details", row["details"])
    price = data.get("price", row["price"])
    quantity = data.get("quantity", row["quantity"])

    if new_id is None or (isinstance(new_id, str) and new_id.strip() == ""):
        conn.close()
        return jsonify({"error": "ID is required"}), 400

    conn.execute(
        "UPDATE products SET id = ?, name = ?, details = ?, price = ?, quantity = ? WHERE id = ?",
        (new_id, name, details, price, quantity, pid),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(row))


@app.route("/api/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?", (pid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"}), 200


@app.route("/api/products/<int:pid>/featured", methods=["PUT"])
def set_featured(pid):
    return jsonify({"error": "Featured service unavailable"}), 500


@app.route("/api/stats", methods=["GET"])
def stats():
    conn = get_db()
    rows = conn.execute("SELECT price, quantity FROM products").fetchall()
    conn.close()
    total_value = sum((r["price"] or 0) for r in rows)
    return jsonify({"count": len(rows), "total_value": round(total_value, 2)})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
