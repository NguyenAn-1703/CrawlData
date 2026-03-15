from PyQt6.QtCore import (QThread, QDate, QObject)
from PyQt6.QtCore import pyqtSignal
from crawl_worker import (CrawlWorker)
from config import (Config)
import pandas as pd

class ThreadManager(QObject):
    _instance = None
    
    def __init__(self, web_url, parser, file_name, start_date: QDate, end_date: QDate):
        super().__init__()
        self.max_thread = Config.MAX_THREADS
        self.web_url = web_url
        self.parser = parser
        self.file_name = file_name
        self.start_date = start_date
        self.end_date = end_date
        self.finished_count = 0
    
    @classmethod
    def get_instance(cls, web_url, parser, file_name, start_date: QDate, end_date: QDate):
        if(cls._instance == None):
            cls._instance = ThreadManager(web_url, parser, file_name, start_date, end_date)
        return cls._instance
            
    def run(self):
        dates = self.get_all_dates(self.start_date, self.end_date)
        self.all_date_length = len(dates)
        chunks = self.split_list(dates, self.max_thread)
        threads = []
        self.workers = []
        for index, chunk in enumerate(chunks):        
            thread = QThread()
            worker = CrawlWorker(index, self.web_url, self.parser, self.file_name, chunk)
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.progress.connect(self.on_worker_progress)
            worker.result_ready.connect(self.collect_data)
            worker.finished.connect(thread.quit)
            worker.finished.connect(self.on_worker_finished)
            
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            
            self.workers.append(worker)
            threads.append(thread)
            thread.start()
        
        return threads #để giữ tham chiếu, tránh garbage collect dọn đi mất

    all_finished = pyqtSignal()
    progress = pyqtSignal(str, int)
    all_data = {}
    thread_logs = {}
    page_count = 0
    
    def on_worker_progress(self, index, text):
        self.page_count += 1
        percent = int(self.page_count / self.all_date_length * 100)
        
        self.thread_logs[index] = text
        message = ""
        for i in sorted(self.thread_logs.keys()):
            message += self.thread_logs[i] + "\n"
        self.progress.emit(message, percent)
    
    def collect_data(self, index, df):
        if(df is not None):
            self.all_data[index]=df

    def on_worker_finished(self): #tất cả các chunk đều xong thì emit
        self.finished_count += 1
        if(self.finished_count == self.max_thread):
            
            ordered_dfs: list[pd.DataFrame] = [self.all_data[i] for i in sorted(self.all_data)] #sắp xếp theo index
            final_df = pd.concat(ordered_dfs, ignore_index=True)
            final_df.to_csv(self.file_name, index=False)
            
            print("Crawl hoàn tất")
            self.all_finished.emit()

    def split_list(self, data, n): #chia mảng
        size = len(data) // n
        chunks = []

        for i in range(n):
            start = i * size
            end = (i + 1) * size if i < n - 1 else len(data)
            chunks.append(data[start:end])

        return chunks
    
    def get_all_dates(self, start_date: QDate, end_date: QDate):
        result : list[QDate] = []
        current = QDate(start_date)
        while(current <= end_date):
            result.append(current)
            current = current.addDays(1)
        
        return result
        