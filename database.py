import sqlite3


def create_table():
    conn = sqlite3.connect("Inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS Inventory (
            part_number TEXT PRIMARY KEY,
            quantity INTEGER,
            description TEXT) """
    )
    conn.commit()
    conn.close()


def fetch_inventory():
    conn = sqlite3.connect("Inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Inventory")
    part_numbers = cursor.fetchall()
    conn.close()
    return part_numbers


def insert_part_numbers(part_number, quantity, description):
    conn = sqlite3.connect("Inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Inventory (part_number, quantity, description) VALUES (?, ?, ?)",
        (part_number, quantity, description),
    )
    conn.commit()
    conn.close()


def delete_inventory(part_number):
    conn = sqlite3.connect("Inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Inventory WHERE part_number = ?", (part_number,))
    conn.commit()
    conn.close()


def delete_all_inventory():
    conn = sqlite3.connect("Inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Inventory")
    conn.commit()
    conn.close()


def update_inventory(
    part_number,
    quantity,
    description,
):
    conn = sqlite3.connect("Inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Inventory SET quantity = ?, description = ? WHERE part_number = ?",
        (
            quantity,
            description,
            part_number,
        ),
    )
    conn.commit()
    conn.close()


def search(option, value):
    conn = sqlite3.connect("Inventory.db")
    cursor = conn.cursor()
    query = f'SELECT * FROM Inventory WHERE "{option}" = ?'
    cursor.execute(query, (value,))
    results = cursor.fetchall()
    conn.close()
    return results


def part_numbers_exists(part_number):
    conn = sqlite3.connect("Inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM Inventory WHERE part_number = ?", (part_number,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] > 0


create_table()

# Example usage
# insert_part_number('12345', 10, 'Sample part')
