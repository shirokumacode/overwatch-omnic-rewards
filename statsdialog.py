from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from datetime import datetime, timedelta

class StatsDialog(QDialog):

    def __init__(self, history_data, account_id, icon_owl, icon_owc, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Stats/History")
        self.setWindowIcon(icon_owl)
        
        self.stats_owl = [0,0,0]
        self.stats_owc = [0,0,0]

        self.process_file(history_data, account_id)

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
        inner_layout.addWidget(QLabel(str(self.stats_owl[0]) + " min"), 0, 2)
        inner_layout.addWidget(QLabel(str(self.stats_owl[1]) + " min"), 1, 2)
        inner_layout.addWidget(QLabel(str(self.stats_owl[2]) + " min"), 2, 2)
        inner_layout.addWidget(QLabel(str(round(self.stats_owl[0]/60, 2)) + "h"), 0, 3)
        inner_layout.addWidget(QLabel(str(round(self.stats_owl[1]/60, 2)) + "h"), 1, 3)
        inner_layout.addWidget(QLabel(str(round(self.stats_owl[2]/60, 2)) + "h"), 2, 3)
        inner_layout.addWidget(QLabel(str(int(self.stats_owl[0]/60)*5) + " tokens"), 0, 4)
        inner_layout.addWidget(QLabel(str(int(self.stats_owl[1]/60)*5) + " tokens"), 1, 4)
        inner_layout.addWidget(QLabel(str(int(self.stats_owl[2]/60)*5) + " tokens"), 2, 4)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setLineWidth(3)
        inner_layout.addWidget(line, 3, 0, 2, 5)

        inner_layout.addWidget(label_owc, 5, 0, 3, 1)
        inner_layout.addWidget(QLabel("Last 24h"), 5, 1)
        inner_layout.addWidget(QLabel("Last 7d"), 6, 1)
        inner_layout.addWidget(QLabel("This month"), 7, 1)
        inner_layout.addWidget(QLabel(str(self.stats_owc[0]) + " min"), 5, 2)
        inner_layout.addWidget(QLabel(str(self.stats_owc[1]) + " min"), 6, 2)
        inner_layout.addWidget(QLabel(str(self.stats_owc[2]) + " min"), 7, 2)
        inner_layout.addWidget(QLabel(str(round(self.stats_owc[0]/60, 2)) + "h"), 5, 3)
        inner_layout.addWidget(QLabel(str(round(self.stats_owc[1]/60, 2)) + "h"), 6, 3)
        inner_layout.addWidget(QLabel(str(round(self.stats_owc[2]/60, 2)) + "h"), 7, 3)

        outer_layout = QVBoxLayout()
        outer_layout.addLayout(inner_layout)
        outer_layout.addWidget(btn_box)
        outer_layout.setSpacing(20)

        self.setLayout(outer_layout)

        self.setFixedSize(self.sizeHint())
        
    def process_file(self, history_data, accountid):
        range_day = datetime.now().astimezone()-timedelta(hours=24)
        range_week = datetime.now().astimezone()-timedelta(days=7)
        current_month = datetime.now().astimezone().month

        for row in history_data:
            try:
                if row['Account'] == accountid:
                    if datetime.fromisoformat(row['Timestamp']) > range_day:
                        if row['Type'] == 'owl':
                            self.stats_owl[0] += int(row['Minutes'])
                            self.stats_owl[1] += int(row['Minutes'])
                        elif row['Type'] == 'owc':
                            self.stats_owc[0] += int(row['Minutes'])
                            self.stats_owc[1] += int(row['Minutes'])
                    elif datetime.fromisoformat(row['Timestamp']) > range_week:
                        if row['Type'] == 'owl':
                            self.stats_owl[1] += int(row['Minutes'])
                        elif row['Type'] == 'owc':
                            self.stats_owc[1] += int(row['Minutes'])
                    if datetime.fromisoformat(row['Timestamp']).month == current_month:
                        if row['Type'] == 'owl':
                            self.stats_owl[2] += int(row['Minutes'])
                        elif row['Type'] == 'owc':
                            self.stats_owc[2] += int(row['Minutes'])
            except Exception as e:
                continue

if __name__ == "__main__":
    import io, os, csv
    app = QApplication([])
    icon_owl = QIcon(os.path.join("icons", "iconowl.png"))
    icon_owc = QIcon(os.path.join("icons", "iconowc.png"))
    fake_data = io.StringIO("Timestamp,Account,Type,Title,Minutes\n"
                            "2021-07-01T10:22:12.588667+01:00,111111111,owl,FakeTitleOWL1,65\n"
                            "2021-06-27T10:22:12.588667+01:00,111111111,owl,FakeTitleOWL2,45\n"
                            "2021-06-15T19:22:12.588667+01:00,111111111,owl,FakeTitleOWL3,45\n"
                            "2021-07-01T19:22:12.588667+01:00,111111111,owc,FakeTitleOWC1,35\n"
                            "2021-06-27T19:22:12.588667+01:00,111111111,owc,FakeTitleOWC2,15\n"
                            "2021-06-15T19:22:12.588667+01:00,111111111,owc,FakeTitleOWC3,20\n")
    account_id = "111111111"
    history_data = csv.DictReader(fake_data)
    dialog = StatsDialog(history_data, account_id, icon_owl, icon_owc)
    dialog.exec_()