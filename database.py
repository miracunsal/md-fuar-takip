import sqlite3
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "md_fuar.db"))
BACKUP_DIR = os.environ.get("BACKUP_DIR", os.path.join(BASE_DIR, "backups"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT UNIQUE NOT NULL,
            firm_name TEXT DEFAULT '',
            yovmiye REAL DEFAULT 0,
            amount_received REAL DEFAULT 0,
            worker_expense REAL DEFAULT 0,
            net_profit REAL DEFAULT 0,
            payment_status TEXT DEFAULT 'PAID',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sütun Kontrolü (payment_status yoksa ekle - Schema Migration)
    cursor.execute("PRAGMA table_info(daily_records)")
    columns = [row[1] for row in cursor.fetchall()]
    if "payment_status" not in columns:
        cursor.execute("ALTER TABLE daily_records ADD COLUMN payment_status TEXT DEFAULT 'PAID'")
        
    conn.commit()
    conn.close()

def save_or_update_record(record_date, firm_name, yovmiye, amount_received, worker_expense, payment_status="PAID", notes=""):
    net_profit = float(amount_received or 0) - float(worker_expense or 0)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO daily_records (record_date, firm_name, yovmiye, amount_received, worker_expense, net_profit, payment_status, notes, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(record_date) DO UPDATE SET
            firm_name = excluded.firm_name,
            yovmiye = excluded.yovmiye,
            amount_received = excluded.amount_received,
            worker_expense = excluded.worker_expense,
            net_profit = excluded.net_profit,
            payment_status = excluded.payment_status,
            notes = excluded.notes,
            updated_at = CURRENT_TIMESTAMP
    """, (record_date, firm_name, float(yovmiye or 0), float(amount_received or 0), float(worker_expense or 0), float(net_profit or 0), payment_status, notes))
    conn.commit()
    conn.close()

def get_record(record_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_records WHERE record_date = ?", (record_date,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def delete_record(record_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_records WHERE record_date = ?", (record_date,))
    conn.commit()
    conn.close()

def get_monthly_summary(year, month):
    month_str = f"{year:04d}-{month:02d}-%"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as record_count,
            COALESCE(SUM(yovmiye), 0) as total_yovmiye,
            COALESCE(SUM(amount_received), 0) as total_received,
            COALESCE(SUM(worker_expense), 0) as total_expense,
            COALESCE(SUM(net_profit), 0) as total_net
        FROM daily_records
        WHERE record_date LIKE ?
    """, (month_str,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)

def get_recorded_dates_in_month(year, month):
    month_str = f"{year:04d}-{month:02d}-%"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT record_date, payment_status FROM daily_records WHERE record_date LIKE ?", (month_str,))
    rows = cursor.fetchall()
    conn.close()
    return {row["record_date"]: row["payment_status"] for row in rows}

def search_records(query="", limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    search_pattern = f"%{query}%"
    cursor.execute("""
        SELECT * FROM daily_records 
        WHERE firm_name LIKE ? OR notes LIKE ? OR record_date LIKE ?
        ORDER BY record_date DESC
        LIMIT ?
    """, (search_pattern, search_pattern, search_pattern, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_firm_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            firm_name,
            COUNT(*) as total_jobs,
            COALESCE(SUM(yovmiye), 0) as total_yovmiye,
            COALESCE(SUM(amount_received), 0) as total_received,
            COALESCE(SUM(worker_expense), 0) as total_expense,
            COALESCE(SUM(net_profit), 0) as total_net,
            SUM(CASE WHEN payment_status = 'PENDING' THEN 1 ELSE 0 END) as pending_count,
            SUM(CASE WHEN payment_status = 'PARTIAL' THEN 1 ELSE 0 END) as partial_count
        FROM daily_records
        WHERE firm_name IS NOT NULL AND TRIM(firm_name) != ''
        GROUP BY firm_name
        ORDER BY total_received DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_weekly_records(start_date_str, end_date_str, firm_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    if firm_name and firm_name.strip():
        cursor.execute("""
            SELECT * FROM daily_records 
            WHERE record_date >= ? AND record_date <= ? AND firm_name LIKE ?
            ORDER BY record_date ASC
        """, (start_date_str, end_date_str, f"%{firm_name.strip()}%"))
    else:
        cursor.execute("""
            SELECT * FROM daily_records 
            WHERE record_date >= ? AND record_date <= ?
            ORDER BY record_date ASC
        """, (start_date_str, end_date_str))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def auto_backup_db():
    try:
        if not os.path.exists(DB_PATH):
            return None
        
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"md_fuar_backup_{timestamp}.db")
        
        shutil.copy2(DB_PATH, backup_file)
        
        # Son 30 yedekten eskisini temizle
        backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".db")])
        if len(backups) > 30:
            for old_backup in backups[:-30]:
                try:
                    os.remove(old_backup)
                except Exception as e:
                    print("Eski yedek silme hatası:", e)
                    
        return backup_file
    except Exception as ex:
        print("Auto backup notice:", ex)
        return None
