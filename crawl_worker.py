from PyQt6.QtCore import (QObject, pyqtSignal, QDate)
# from datetime import datetime, timedelta
from PyQt6.QtCore import pyqtSignal
from crawl_processor import CrawlProcessor
import pandas as pd
from urllib.parse import urljoin

class CrawlWorker(QObject):
    def __init__(self, index, web_url, parser, file_name, dates: list[QDate]):
        super().__init__()
        self.index = index
        self.web_url = web_url
        self.parser = parser
        self.file_name = file_name
        self.dates = dates
    
    finished = pyqtSignal()
    progress = pyqtSignal(int, str)
    result_ready = pyqtSignal(int, object) #trả kế quả để nối với thread khác
    urls = []
    
    
    def run(self):
        result = self.crawl()
        self.result_ready.emit(self.index, result)
        self.finished.emit()
        
    def crawl(self):   
        dfs: list[pd.DataFrame] = []
    
        crawler_processor = CrawlProcessor()
        
        for date in self.dates:
            date_str = date.toString("yyyy-MM-dd")
            url = urljoin(self.web_url, f"{date_str}.html")
            
            self.progress.emit(
                self.index,
                f"Thread {self.index}: đang crawl {date_str}"
            )

            df = crawler_processor.start_crawl(url, self.parser)
            
            self.urls.append(url)
            if(df is not None):
                dfs.append(df)
            else:
                print("df bị none")
             
             
        if len(dfs) == 0:
            return None   
        
        datacrawl = pd.concat(dfs, ignore_index=True)
        
        return datacrawl
        

            

    