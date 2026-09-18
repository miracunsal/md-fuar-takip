import os
import subprocess
import sys

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_script = os.path.join(base_dir, "app.py")
    assets_dir = os.path.join(base_dir, "assets")
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=MDFuarTakipSistemi",
        "--hidden-import=openpyxl",
        "--hidden-import=et_xmlfile",
        f"--add-data={assets_dir}{os.path.pathsep}assets",
        app_script
    ]
    
    print("PyInstaller derlemesi başlatılıyor (Faz 2):")
    print(" ".join(cmd))
    
    result = subprocess.run(cmd, cwd=base_dir)
    if result.returncode == 0:
        print("\n[BAŞARILI] Güncellenmiş MDFuarTakipSistemi.exe başarıyla oluşturuldu!")
        print(f"Konum: {os.path.join(base_dir, 'dist', 'MDFuarTakipSistemi')}")
    else:
        print("\n[HATA] Derleme sırasında bir hata oluştu.")

if __name__ == "__main__":
    build()
