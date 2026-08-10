import sqlite3

def init_db():
    # Connects to local SQLite database (creates data.db file automatically if missing)
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # 1. Create Employees Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        salary REAL NOT NULL
    )
    """)

    # 2. Create Sales Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        sale_date TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
    """)

    # Reset tables to avoid duplicate rows during repeated test runs
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM employees")

    # 3. Seed Sample Employee Data
    employees = [
        ("Alice Smith", "Engineering", 95000),
        ("Bob Jones", "Engineering", 88000),
        ("Charlie Brown", "Sales", 65000),
        ("Diana Prince", "Sales", 72000),
        ("Evan Wright", "Marketing", 60000)
    ]
    cursor.executemany(
        "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)", 
        employees
    )

    # 4. Seed Sample Sales Data
    sales = [
        (1, 1500.00, "2026-01-15"),
        (1, 2300.00, "2026-02-20"),
        (3, 5000.00, "2026-01-10"),
        (3, 4200.00, "2026-03-05"),
        (4, 6100.00, "2026-02-18"),
        (5, 1200.00, "2026-03-12")
    ]
    cursor.executemany(
        "INSERT INTO sales (employee_id, amount, sale_date) VALUES (?, ?, ?)", 
        sales
    )

    # Persist changes to disk and close connection
    conn.commit()
    conn.close()
    print("Database data.db created and populated successfully!")

if __name__ == "__main__":
    init_db()