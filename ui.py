from PyQt6.QtWidgets import (
    QWidget, QLabel,
    QLineEdit, QPushButton, QComboBox,
    QGridLayout, QDateEdit
)

from PyQt6.QtCore import (QDate)

from crawl_processor import (
    CrawlProcessor
)

from pathlib import Path

from config import (Config)

# from processor import (Processor)
from thread_manager import (ThreadManager)
from crawl_worker import CrawlWorker
from dialog import SimpleDialog
from dialog import ProgressDialog

STYLE = """
QWidget {
    font-size: 20px;
}
"""
class CrawlerUI(QWidget):
    _instance = None
    # crawler = CrawlerProcessor.get_instance()
    # processor = Processor.get_instace()
    # thread_manager = ThreadManager.get_instance()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.setStyleSheet(STYLE)
        self.set_data_input()
    
    @classmethod
    def get_instance(cls):
        if(cls._instance == None):
            cls._instance = CrawlerUI()
        return cls._instance
        
    def init_ui(self):
        self.setWindowTitle("Simple Web Crawler")
        self.setFixedSize(300,200)
    
    def create_widgets(self):
        self.url_container = QWidget()
        self.urlLayout = QGridLayout()
        self.url_container.setLayout(self.urlLayout)
        self.url_label = QLabel("URL:")
        self.url_input = QLineEdit()

        self.urlLayout.addWidget(self.url_label, 0, 0)
        self.urlLayout.addWidget(self.url_input, 0, 1)

        self.parser_container = QWidget()
        self.parser_layout = QGridLayout()
        self.parser_container.setLayout(self.parser_layout)
        self.parser_label = QLabel("Parser:")
        self.parser_combo = QComboBox()
        self.parser_combo.addItems(["html5lib", "lxml"])
                
        self.parser_layout.addWidget(self.parser_label, 0, 0)
        self.parser_layout.addWidget(self.parser_combo, 0, 1)
        
        self.parser_layout.setColumnStretch(0, 0)
        self.parser_layout.setColumnStretch(1, 1) 

        self.file_container = QWidget()
        self.file_layout = QGridLayout()
        self.file_container.setLayout(self.file_layout)
        self.file_label = QLabel("CSV File:")
        self.file_input = QLineEdit()
        self.file_layout.addWidget(self.file_label, 0, 0)
        self.file_layout.addWidget(self.file_input, 0, 1)

        self.crawl_button = QPushButton("Start Crawl")
        self.crawl_button.clicked.connect(self.onClickBtnCrawl)
        
        self.start_date_container = QWidget()
        self.start_date_layout = QGridLayout()
        self.start_date_container.setLayout(self.start_date_layout)
        self.start_date_label = QLabel("Start date:")
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        
        self.start_date_layout.addWidget(self.start_date_label, 0, 0)
        self.start_date_layout.addWidget(self.start_date_input, 0, 1)
        self.start_date_layout.setColumnStretch(0, 0)
        self.start_date_layout.setColumnStretch(1, 1)
        
        self.end_date_container = QWidget()
        self.end_date_layout = QGridLayout()
        self.end_date_container.setLayout(self.end_date_layout)
        self.end_date_label = QLabel("End date:")
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        
        self.end_date_layout.addWidget(self.end_date_label, 0, 0)
        self.end_date_layout.addWidget(self.end_date_input, 0, 1)
        self.end_date_layout.setColumnStretch(0, 0)
        self.end_date_layout.setColumnStretch(1, 1)

    def create_layout(self):
        layout = QGridLayout()

        layout.addWidget(self.url_container, 0, 0)
        layout.addWidget(self.parser_container, 0, 1)
        layout.addWidget(self.file_container, 0, 2)
        layout.addWidget(self.start_date_container, 1, 0)
        layout.addWidget(self.end_date_container, 1, 1)
        layout.addWidget(self.crawl_button, 2, 1)
        
        for i in range(layout.columnCount()):
            layout.setColumnStretch(i, 1)
        
        layout.setRowStretch(3, 1)

        self.setLayout(layout)

    def onClickBtnCrawl(self):
        url = self.url_input.text()
        parser = self.parser_combo.currentText()
        file = self.file_input.text()
        file_name = Path(file)
        file_name = file_name.with_suffix(".csv")
        start_date = self.start_date_input.date()
        end_date = self.end_date_input.date()
        print(url)
        print(parser)
        print(file_name)
        print(start_date)
        print(end_date)
        
        if(not self.validate(start_date, end_date)):
            return
                
        # dialog loading
        self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.show()

        # thread
        self.thread_manager = ThreadManager.get_instance(url, parser, file_name, start_date, end_date)
        self.threads = self.thread_manager.run()
        self.thread_manager.progress.connect(self.update_progress)
        self.thread_manager.all_finished.connect(self.crawl_done)
        
        # self.crawl_processor = CrawlProcessor()
        # self.crawl_processor.start_crawl(url, parser, file_name)   
        
    def validate(self, start_date: QDate, end_date: QDate):
        max_year = Config.MAX_YEARS
        if(end_date > start_date.addYears(max_year)):
            dialog = SimpleDialog(self, f"Thời gian không được quá {max_year} năm")
            dialog.exec()
            return False
        return True            
        
    
    def crawl_done(self):
        self.progress_dialog.close()
        dialog = SimpleDialog(self, "Crawl dữ liệu thành công")
        dialog.exec()
        
    def update_progress(self, str, percent):
        self.progress_dialog.update_text(str)
        self.progress_dialog.set_progress(percent)
        
    def set_data_input(self):
        self.url_input.setText("https://giavang.org/trong-nuoc/sjc/lich-su/")
        self.file_input.setText("ab")
        self.start_date_input.setDate(QDate(2024, 1, 1))
        self.end_date_input.setDate(QDate(2024, 12, 31))
        
        
        