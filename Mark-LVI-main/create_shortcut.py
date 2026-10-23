import sys
from pathlib import Path
from win32com.client import Dispatch

desktop = Path(r"C:\Users\HP\Desktop")
script = desktop / "Mark-LVI-main" / "main.py"
pythonw = Path(sys.executable).parent / "pythonw.exe"
target = str(pythonw if pythonw.exists() else sys.executable)
ico = str(desktop / "Mark-LVI-main" / "config" / "jarvis.ico")
lnk = str(desktop / "J.A.R.V.I.S.lnk")

sh = Dispatch("WScript.Shell")
sc = sh.CreateShortCut(lnk)
sc.TargetPath = target
sc.Arguments = f'-X utf8 "{script}"'
sc.WorkingDirectory = str(script.parent)
sc.Description = "J.A.R.V.I.S AI Assistant"
sc.IconLocation = ico
sc.Save()
print("Shortcut created at:", lnk)
