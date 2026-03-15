import sys
from PyQt6.QtWidgets import (
    QApplication
)
from ui import (CrawlerUI)

app = QApplication(sys.argv)

window = CrawlerUI.get_instance()

window.showMaximized()

sys.exit(app.exec())