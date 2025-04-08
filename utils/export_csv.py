# utils/export_csv.py
import csv
from database.db import get_connection

def export_to_csv():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bom")
    rows = cursor.fetchall()
    with open("bom_export.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Mã SP", "Tên SP", "Cycle", "Trạng thái", "Nhân công", "Ver", "Bộ phận"])
        for row in rows:
            writer.writerow(row[1:])
    conn.close()
