from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

import os, csv

import logging
logger = logging.getLogger(__name__)

@dataclass
class Record:
    contenders: bool
    min_watched: int
    title: str
    accountid: str

class Stats():
    def __init__(self, location:str):
        self.file_path = location
        self.record = None 

    def get_record(self, contenders:bool, min_watched:int, title:str, accountid:str) -> Optional[Record]:
        return self.record

    def set_record(self, contenders:bool, min_watched:int, title:str, accountid:str):
        self.record = Record(contenders, min_watched, title, accountid)
    
    def write_record(self):
        if self.record:
            logger.info("Writting history record")
            self._write()
            self.record = None
        
    def _write(self):
        if os.path.isfile(self.file_path):
            write_header = False 
            write_mode = 'a'
        else:
            write_header = True
            write_mode = 'w'

        contenders = 'owc' if self.record.contenders else 'owl'
        timestamp = datetime.now().astimezone().isoformat()

        with open(self.file_path, write_mode) as f:
            writer = csv.writer(f)
            if write_header:
               writer.writerow(['Timestamp', 'Account', 'Type', 'Title', 'Minutes'])
            writer.writerow([
                timestamp,
                self.record.accountid, 
                contenders, 
                self.record.title, 
                self.record.min_watched
            ])
        
    def show(self, icon_owl:QIcon, icon_owc:QIcon, accountid:str):
        logger.info("Show stats")
        stats_owl = stats_owc = [0,0,0]
        
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r', newline='') as history_file:
                stats_data = csv.DictReader(history_file)
                logger.info("Loaded history file")
                stats_owl, stats_owc = self._process_file(stats_data, accountid)

        self.stats_dialog = StatsDialog(stats_owl, stats_owc, icon_owl, icon_owc)
        self.stats_dialog.show()
        self.stats_dialog.raise_()
        self.stats_dialog.activateWindow()
        self.stats_dialog.finished.connect(self.stats_dialog.deleteLater)

    def _process_file(self, history_data:dict, accountid:str) -> (list,list):
        range_day = datetime.now().astimezone()-timedelta(hours=24)
        range_week = datetime.now().astimezone()-timedelta(days=7)
        current_month = datetime.now().astimezone().month

        stats_owl = [0,0,0]
        stats_owc = [0,0,0]

        for row in history_data:
            try:
                if row['Account'] == accountid:
                    if datetime.fromisoformat(row['Timestamp']) > range_day:
                        if row['Type'] == 'owl':
                            stats_owl[0] += int(row['Minutes'])
                            stats_owl[1] += int(row['Minutes'])
                        elif row['Type'] == 'owc':
                            stats_owc[0] += int(row['Minutes'])
                            stats_owc[1] += int(row['Minutes'])
                    elif datetime.fromisoformat(row['Timestamp']) > range_week:
                        if row['Type'] == 'owl':
                            stats_owl[1] += int(row['Minutes'])
                        elif row['Type'] == 'owc':
                            stats_owc[1] += int(row['Minutes'])
                    if datetime.fromisoformat(row['Timestamp']).month == current_month:
                        if row['Type'] == 'owl':
                            stats_owl[2] += int(row['Minutes'])
                        elif row['Type'] == 'owc':
                            stats_owc[2] += int(row['Minutes'])
            except Exception:
                continue

        return stats_owl, stats_owc

class StatsDialog(QDialog):

    def __init__(self, stats_owl:list, stats_owc:list, icon_owl:QIcon, icon_owc:QIcon, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Stats/History")
        self.setWindowIcon(icon_owl)

        label_owl = QLabel("<h3>Overwatch League</h3>")
        label_owl.setPixmap(icon_owl.pixmap(50,50))
        label_owc = QLabel("<h3>Overwatch Contenders</h3>")
        label_owc.setPixmap(icon_owc.pixmap(50,50))

        btn_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        btn_box.rejected.connect(self.reject)

        inner_layout = QGridLayout()

        inner_layout.addWidget(label_owl, 0, 0, 3, 1)
        inner_layout.addWidget(QLabel("Last 24h"), 0, 1)
        inner_layout.addWidget(QLabel("Last 7d"), 1, 1)
        inner_layout.addWidget(QLabel("This month"), 2, 1)
        inner_layout.addWidget(QLabel(str(stats_owl[0]) + " min"), 0, 2)
        inner_layout.addWidget(QLabel(str(stats_owl[1]) + " min"), 1, 2)
        inner_layout.addWidget(QLabel(str(stats_owl[2]) + " min"), 2, 2)
        inner_layout.addWidget(QLabel(str(round(stats_owl[0]/60, 2)) + "h"), 0, 3)
        inner_layout.addWidget(QLabel(str(round(stats_owl[1]/60, 2)) + "h"), 1, 3)
        inner_layout.addWidget(QLabel(str(round(stats_owl[2]/60, 2)) + "h"), 2, 3)
        inner_layout.addWidget(QLabel(str(int(stats_owl[0]/60)*5) + " tokens"), 0, 4)
        inner_layout.addWidget(QLabel(str(int(stats_owl[1]/60)*5) + " tokens"), 1, 4)
        inner_layout.addWidget(QLabel(str(int(stats_owl[2]/60)*5) + " tokens"), 2, 4)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setLineWidth(3)
        inner_layout.addWidget(line, 3, 0, 2, 5)

        inner_layout.addWidget(label_owc, 5, 0, 3, 1)
        inner_layout.addWidget(QLabel("Last 24h"), 5, 1)
        inner_layout.addWidget(QLabel("Last 7d"), 6, 1)
        inner_layout.addWidget(QLabel("This month"), 7, 1)
        inner_layout.addWidget(QLabel(str(stats_owc[0]) + " min"), 5, 2)
        inner_layout.addWidget(QLabel(str(stats_owc[1]) + " min"), 6, 2)
        inner_layout.addWidget(QLabel(str(stats_owc[2]) + " min"), 7, 2)
        inner_layout.addWidget(QLabel(str(round(stats_owc[0]/60, 2)) + "h"), 5, 3)
        inner_layout.addWidget(QLabel(str(round(stats_owc[1]/60, 2)) + "h"), 6, 3)
        inner_layout.addWidget(QLabel(str(round(stats_owc[2]/60, 2)) + "h"), 7, 3)

        outer_layout = QVBoxLayout()
        outer_layout.addLayout(inner_layout)
        outer_layout.addWidget(btn_box)
        outer_layout.setSpacing(20)

        self.setLayout(outer_layout)

        self.setFixedSize(self.sizeHint())

if __name__ == "__main__":
    import io, os, csv
    app = QApplication([])
    icon_owl = QIcon(os.path.join("icons", "iconowl.png"))
    icon_owc = QIcon(os.path.join("icons", "iconowc.png"))
    
    # accountid = "123456789"
    # stats = Stats('fakehistory.csv')
    # stats.write(contenders=False, min_watched=20, title="Fake OWL 1", accountid=accountid)
    # stats.write(contenders=False, min_watched=40, title="Fake OWL 2", accountid=accountid)
    # stats.write(contenders=True, min_watched=10, title="Fake OWC 1", accountid=accountid)
    # stats.write(contenders=True, min_watched=20, title="Fake OWC 2", accountid=accountid)
    # stats.show(icon_owl, icon_owc, accountid)
    
    dialog = StatsDialog([12,56,78], [24,67,100], icon_owl, icon_owc)
    dialog.exec_()