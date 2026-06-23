# Product Management — CRUD demo (QA interview)

A simple web application for managing products / car parts (Create / Read / Update / Delete).
Built to evaluate a QA candidate's testing skills during an interview.

- **Backend:** Python + Flask
- **Database:** SQLite (created automatically)
- **Frontend:** a single HTML file with vanilla JS

## Running

Requires **Python 3.9+**. Check whether you have it:

```bash
python3 --version
```

If it prints a version (3.9 or newer), you're ready. If the command is not found,
install Python from [python.org/downloads](https://www.python.org/downloads/)
(on macOS you can also run `brew install python`), then open a new terminal.

Then, from the project folder:

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Open in the browser: **http://localhost:5001**

Demo login: **admin / admin123**

The `products.db` file is created automatically with a few sample products.
To start fresh, delete `products.db` and run again.

## API endpoints

| Method | Path                          | Description                |
|--------|-------------------------------|----------------------------|
| POST   | `/api/login`                  | Log in                     |
| GET    | `/api/products`               | All products (`?search=`)  |
| GET    | `/api/products/<id>`          | A single product           |
| POST   | `/api/products`               | Create                     |
| PUT    | `/api/products/<id>`          | Update                     |
| DELETE | `/api/products/<id>`          | Delete                     |
| PUT    | `/api/products/<id>/featured` | Toggle the featured flag   |
| GET    | `/api/stats`                  | Statistics                 |

An OpenAPI spec (`qa-crud-api.yaml`) is included and can be imported into Postman.
