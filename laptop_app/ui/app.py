"""Application factory retained for embedders and tests."""
from PyQt6.QtWidgets import QApplication
from pathlib import Path
def create_application(argv=None):
    app=QApplication(argv or [])
    stylesheet=Path(__file__).parent/'styles'/'global.qss'
    if stylesheet.exists(): app.setStyleSheet(stylesheet.read_text(encoding='utf-8'))
    return app
