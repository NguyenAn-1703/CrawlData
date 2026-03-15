from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QWidget, QPlainTextEdit, QProgressBar
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QProgressDialog
from PyQt6.QtCore import Qt

class SimpleDialog(QDialog):

    def __init__(self, parent: QWidget, message="", title="Thông báo"):
        super().__init__(parent)

        self.setWindowTitle(title)
        layout = QVBoxLayout()

        self.label = QLabel(message)
        layout.addWidget(self.label)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout.addWidget(self.ok_button)

        self.setLayout(layout)
    

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Đang xử lý")
        self.setMinimumHeight(250)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        self.label = QLabel("Đang crawl dữ liệu...")
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.btn_detail = QPushButton("Chi tiết ▼")
        layout.addWidget(self.btn_detail)

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setVisible(False)
        self.log_box.setMinimumHeight(150)
        self.log_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout.addWidget(self.log_box)

        self.btn_detail.clicked.connect(self.toggle_detail)
        
    def toggle_detail(self):

        visible = self.log_box.isVisible()

        self.log_box.setVisible(not visible)

        if visible:
            self.btn_detail.setText("Chi tiết ▼")
        else:
            self.btn_detail.setText("Ẩn chi tiết ▲")
    
    def update_text(self, text):
        self.log_box.setPlainText(text)
        
    def set_progress(self, value):
        self.progress.setValue(value)