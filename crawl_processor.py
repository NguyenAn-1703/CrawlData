import requests

from bs4 import BeautifulSoup
from bs4.element import (ResultSet, Tag)

import pandas as pd

class CrawlProcessor:
    def start_crawl(self, url, parser):
        self.url = url
        self.parser = parser
        self.getHtml()
        
        if(self.findTable()):
            self.parse_html_table()
            result = self.add_to_dataframe()
            return result
        else:
            return None
        
    def getHtml(self):
        self.response = requests.get(self.url, timeout=10)
        html = self.response.text
        self.soup = BeautifulSoup(html, self.parser) #parse sang DOM
        
        
    def findTable(self):
        box = self.soup.find("div", class_="box-content")
        # self.target_table = None

        if box and "Không tìm thấy dữ liệu giá vàng" in box.get_text():
            print("Không có dữ liệu -> bỏ qua")
            return False

        print(f"{self.url}Tìm thấy")
        # Tìm bảng cần crawl
        for table in self.soup.select("table.table.table-bordered.table-hover.table-striped"): #lấy theo class của table
            header = table.select_one("thead th:last-child")    #lấy tên cột cuối cùng có tên là "Thời gian cập nhật"
            
            if header and "Thời gian cập nhật" in header.text:
                self.target_table = table
                break
        
        return True
        
    def parse_html_table(self):
        rows = self.target_table.select("tr")

        grid = [] #lưu ma trận trả về
        rowspan_map = {} #dict lưu các giá trị rowspan của table

        for r, row in enumerate(rows): #duyệt lấy key và value
            cells = row.select("td, th")
            row_data = []
            c = 0

            for cell in cells:

                # nếu vị trí này bị rowspan từ dòng trên
                while (r, c) in rowspan_map:
                    row_data.append(rowspan_map[(r, c)])
                    c += 1

                text = cell.get_text(strip=True)
                row_data.append(text)

                rowspan = int(cell.get("rowspan", 1)) #lấy giá trị rowspan, mặc định là 1

                # lưu rowspan cho các dòng sau
                if rowspan > 1:
                    for i in range(1, rowspan):
                        rowspan_map[(r + i, c)] = text #ma trận ở các ô span sẽ có giá trị text

                c += 1

            # nếu cuối dòng vẫn còn rowspan chưa điền
            while (r, c) in rowspan_map:
                row_data.append(rowspan_map[(r, c)])
                c += 1

            grid.append(row_data)
            
        self.rows_data = grid

        return grid
    
    def add_to_dataframe(self):
        df = pd.DataFrame(self.rows_data) # chuyển mảng vào dataframe để xử lý
        df = df.iloc[1:-1] # bỏ dòng đầu-header và dòng cuối-dòng hiển thị url
        df.columns = ["khu_vuc","loai_vang", "mua_vao", "ban_ra", "thoi_gian_cap_nhat"]
        
    #     df.to_csv(self.file_name + ".csv")   
        return df
            
    