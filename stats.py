from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
import os
import csv

import logging

logger = logging.getLogger(__name__)


@dataclass
class Record:
    contenders: bool
    min_watched: int
    title: str
    accountid: str


class Stats:
    def __init__(self, location: str, icon_owl: QIcon, icon_owc: QIcon):
        self.file_path = location
        self.stats_dialog = StatsDialog(icon_owl, icon_owc)
        self.refresh_stats_timer = QTimer()
        self.record = None

    def get_record(self) -> Optional[Record]:
        return self.record

    def set_record(self, contenders: bool, min_watched: int, title: str, accountid: str):
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

    def show(self, accountid: str):
        logger.info("Opening stats dialog")
        self.stats_account = accountid
        self._update_values()

        self.stats_dialog.show()
        self.stats_dialog.raise_()
        self.stats_dialog.activateWindow()

        self.refresh_stats_timer.setInterval(60000)
        self.refresh_stats_timer.timeout.connect(self._update_values)
        self.refresh_stats_timer.start()
        self.stats_dialog.finished.connect(self.refresh_stats_timer.stop)

    def _update_values(self):
        logger.debug("Updating values on dialog")
        stats_owl, stats_owc = self._get_stats_summary(self.stats_account)
        self.stats_dialog.update_values(stats_owl, stats_owc, self.stats_account)

    def _get_stats_summary(self, accountid):
        stats_data = []

        if self.record:
            stats_data.append({
                    'Timestamp': datetime.now().astimezone().isoformat(),
                    'Account': self.record.accountid,
                    'Type': 'owc' if self.record.contenders else 'owl',
                    'Title': self.record.title,
                    'Minutes': self.record.min_watched
            })

        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r', newline='') as history_file:
                stats_data.extend(csv.DictReader(history_file))
                logger.debug("Loaded history file")

        stats_owl, stats_owc = self._process_data(stats_data, accountid)

        return stats_owl, stats_owc


    def _process_data(self, history_data: list, accountid: str) -> (list, list):
        range_day = datetime.now().astimezone() - timedelta(hours=24)
        range_week = datetime.now().astimezone() - timedelta(days=7)
        current_month = datetime.now().astimezone().month

        stats_owl = [0, 0, 0]
        stats_owc = [0, 0, 0]

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
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Malformed history file at {row} -  {e}")
                continue

        return stats_owl, stats_owc


class StatsDialog(QDialog):

    def __init__(self, icon_owl: QIcon, icon_owc: QIcon, stats_owl=None, stats_owc=None, accountid=None, parent=None):
        super().__init__(parent)

        if stats_owc is None:
            stats_owc = [0, 0, 0]
        if stats_owl is None:
            stats_owl = [0, 0, 0]
        self.setWindowTitle("Stats/History")
        self.setWindowIcon(icon_owl)

        label_owl = QLabel("<h3>Overwatch League</h3>")
        label_owl.setPixmap(icon_owl.pixmap(50, 50))
        label_owc = QLabel("<h3>Overwatch Contenders</h3>")
        label_owc.setPixmap(icon_owc.pixmap(50, 50))

        self.button_layout = QHBoxLayout()
        self.label_account = QLabel()
        self.label_account.setTextFormat(Qt.RichText)
        self.label_account.setText(f"<b> Account: </b> {accountid}" if accountid else '')
        self.button_layout.addWidget(self.label_account)

        btn_box = QDialogButtonBox(QDialogButtonBox.Close)
        btn_box.rejected.connect(self.reject)
        self.button_layout.addWidget(btn_box)

        self.inner_layout = QGridLayout()

        self.inner_layout.addWidget(label_owl, 0, 0, 3, 1)
        self.inner_layout.addWidget(QLabel("Last 24h"), 0, 1)
        self.inner_layout.addWidget(QLabel("Last 7d"), 1, 1)
        self.inner_layout.addWidget(QLabel("This month"), 2, 1)
        self.inner_layout.addWidget(QLabel(str(stats_owl[0]) + " min"), 0, 2)
        self.inner_layout.addWidget(QLabel(str(stats_owl[1]) + " min"), 1, 2)
        self.inner_layout.addWidget(QLabel(str(stats_owl[2]) + " min"), 2, 2)
        self.inner_layout.addWidget(QLabel(str(round(stats_owl[0] / 60, 2)) + "h"), 0, 3)
        self.inner_layout.addWidget(QLabel(str(round(stats_owl[1] / 60, 2)) + "h"), 1, 3)
        self.inner_layout.addWidget(QLabel(str(round(stats_owl[2] / 60, 2)) + "h"), 2, 3)
        self.inner_layout.addWidget(QLabel(str(int(stats_owl[0] / 60) * 5) + " tokens"), 0, 4)
        self.inner_layout.addWidget(QLabel(str(int(stats_owl[1] / 60) * 5) + " tokens"), 1, 4)
        self.inner_layout.addWidget(QLabel(str(int(stats_owl[2] / 60) * 5) + " tokens"), 2, 4)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setLineWidth(3)
        self.inner_layout.addWidget(line, 3, 0, 2, 5)

        self.inner_layout.addWidget(label_owc, 5, 0, 3, 1)
        self.inner_layout.addWidget(QLabel("Last 24h"), 5, 1)
        self.inner_layout.addWidget(QLabel("Last 7d"), 6, 1)
        self.inner_layout.addWidget(QLabel("This month"), 7, 1)
        self.inner_layout.addWidget(QLabel(str(stats_owc[0]) + " min"), 5, 2)
        self.inner_layout.addWidget(QLabel(str(stats_owc[1]) + " min"), 6, 2)
        self.inner_layout.addWidget(QLabel(str(stats_owc[2]) + " min"), 7, 2)
        self.inner_layout.addWidget(QLabel(str(round(stats_owc[0] / 60, 2)) + "h"), 5, 3)
        self.inner_layout.addWidget(QLabel(str(round(stats_owc[1] / 60, 2)) + "h"), 6, 3)
        self.inner_layout.addWidget(QLabel(str(round(stats_owc[2] / 60, 2)) + "h"), 7, 3)

        outer_layout = QVBoxLayout()
        outer_layout.addLayout(self.inner_layout)
        outer_layout.addLayout(self.button_layout)
        outer_layout.setSpacing(20)

        self.setLayout(outer_layout)

        self.setFixedSize(self.sizeHint())

    def update_values(self, stats_owl: list, stats_owc: list, accountid: str):
        self.label_account.setText(f"<b> Account: </b> {accountid}")
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(0, 2).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(1, 2).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(2, 2).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(0, 3).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(1, 3).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(2, 3).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(0, 4).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(1, 4).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(2, 4).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(5, 2).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(6, 2).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(7, 2).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(5, 3).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(6, 3).widget())
        self.inner_layout.removeWidget(self.inner_layout.itemAtPosition(7, 3).widget())
        self.inner_layout.addWidget(QLabel(str(stats_owl[0]) + " min"), 0, 2)
        self.inner_layout.addWidget(QLabel(str(stats_owl[1]) + " min"), 1, 2)
        self.inner_layout.addWidget(QLabel(str(stats_owl[2]) + " min"), 2, 2)
        self.inner_layout.addWidget(QLabel(str(round(stats_owl[0] / 60, 2)) + "h"), 0, 3)
        self.inner_layout.addWidget(QLabel(str(round(stats_owl[1] / 60, 2)) + "h"), 1, 3)
        self.inner_layout.addWidget(QLabel(str(round(stats_owl[2] / 60, 2)) + "h"), 2, 3)
        self.inner_layout.addWidget(QLabel(str(int(stats_owl[0] / 60) * 5) + " tokens"), 0, 4)
        self.inner_layout.addWidget(QLabel(str(int(stats_owl[1] / 60) * 5) + " tokens"), 1, 4)
        self.inner_layout.addWidget(QLabel(str(int(stats_owl[2] / 60) * 5) + " tokens"), 2, 4)
        self.inner_layout.addWidget(QLabel(str(stats_owc[0]) + " min"), 5, 2)
        self.inner_layout.addWidget(QLabel(str(stats_owc[1]) + " min"), 6, 2)
        self.inner_layout.addWidget(QLabel(str(stats_owc[2]) + " min"), 7, 2)
        self.inner_layout.addWidget(QLabel(str(round(stats_owc[0] / 60, 2)) + "h"), 5, 3)
        self.inner_layout.addWidget(QLabel(str(round(stats_owc[1] / 60, 2)) + "h"), 6, 3)
        self.inner_layout.addWidget(QLabel(str(round(stats_owc[2] / 60, 2)) + "h"), 7, 3)

if __name__ == "__main__":
    global stats
    import os, csv
    logging.basicConfig(level=logging.INFO)

    app = QApplication([])
    icon_owl = QIcon(os.path.join("icons", "iconowl.png"))
    icon_owc = QIcon(os.path.join("icons", "iconowc.png"))

    accountid = "123456789"
    stats = Stats('history.csv', icon_owl, icon_owc)
    stats.set_record(contenders=True, min_watched=24, title="Fake OWL test", accountid='123456789')
    stats.show(accountid)

    app.exec_()
