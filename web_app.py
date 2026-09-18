import os
import socket
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import database
import exporter

app = Flask(__name__, template_folder="templates", static_folder="static")

# Veritabanını Başlat ve Otomatik Yedek Al
database.init_db()
database.auto_backup_db()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/assets/<filename>")
def serve_assets(filename):
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    return send_from_directory(assets_dir, filename)

@app.route("/api/record/<record_date>", methods=["GET"])
def get_record(record_date):
    rec = database.get_record(record_date)
    if rec:
        return jsonify({"success": True, "data": rec})
    return jsonify({"success": True, "data": None})

@app.route("/api/record", methods=["POST"])
def save_record():
    data = request.json or {}
    record_date = data.get("record_date")
    if not record_date:
        return jsonify({"success": False, "error": "Tarih bilgisi eksik!"}), 400

    firm_name = data.get("firm_name", "").strip()
    try:
        yovmiye = float(data.get("yovmiye", 0))
    except ValueError:
        yovmiye = 0.0

    try:
        received = float(data.get("amount_received", 0))
    except ValueError:
        received = 0.0

    try:
        expense = float(data.get("worker_expense", 0))
    except ValueError:
        expense = 0.0

    payment_status = data.get("payment_status", "PAID")
    notes = data.get("notes", "").strip()

    database.save_or_update_record(record_date, firm_name, yovmiye, received, expense, payment_status, notes)
    return jsonify({"success": True, "message": "Kayıt kaydedildi."})

@app.route("/api/record/<record_date>", methods=["DELETE"])
def delete_record(record_date):
    database.delete_record(record_date)
    return jsonify({"success": True, "message": "Kayıt silindi."})

@app.route("/api/monthly-summary", methods=["GET"])
def monthly_summary():
    try:
        year = int(request.args.get("year", date.today().year))
        month = int(request.args.get("month", date.today().month))
    except ValueError:
        year = date.today().year
        month = date.today().month

    summary = database.get_monthly_summary(year, month)
    dates_map = database.get_recorded_dates_in_month(year, month)
    return jsonify({"success": True, "summary": summary, "recorded_dates": dates_map})

@app.route("/api/firm-summary", methods=["GET"])
def firm_summary():
    summaries = database.get_firm_summary()
    return jsonify({"success": True, "data": summaries})

@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    records = database.search_records(query)
    return jsonify({"success": True, "data": records})

@app.route("/api/export-excel", methods=["GET"])
def export_excel():
    s_date = request.args.get("start_date")
    e_date = request.args.get("end_date")
    firm_name = request.args.get("firm_name", "").strip()

    if not s_date or not e_date:
        return jsonify({"error": "Başlangıç ve bitiş tarihleri zorunludur."}), 400

    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_exports")
    os.makedirs(temp_dir, exist_ok=True)
    filename = f"MD_Fuar_Raporu_{s_date}_to_{e_date}.xlsx"
    filepath = os.path.join(temp_dir, filename)

    exporter.generate_weekly_excel_report(s_date, e_date, firm_name, filepath)
    return send_file(filepath, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    ip = get_local_ip()
    print("=" * 60)
    print("🚀 MD FUAR TAKİP SİSTEMİ MOBİL WEB SUNUCUSU BAŞLATILDI")
    print(f"📱 Telefonlardan Bağlantı Adresi : http://{ip}:5000")
    print(f"💻 Bilgisayardan Bağlantı Adresi: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
