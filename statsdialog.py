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

        outer_layout = QVBoxLayout()

        label_owl = QLabel("<h3>Overwatch League</h3>")
        label_owl.setPixmap(icon_owl.pixmap(50,50))
        label_owc = QLabel("<h3>Overwatch Contenders</h3>")
        label_owc.setPixmap(icon_owc.pixmap(50,50))

        stats_owl_text1 = (
            f"<p>Last 24h"
            f"<p>Last 7d"
            f"<p>This Month"
        )
        stats_owl_text2 = (
            f"<p>{self.stats_owl[0]} min - {round(self.stats_owl[0]/60, 2)}h - {int(self.stats_owl[0]/60)*5} tokens \n"
            f"<p>{self.stats_owl[1]} min - {round(self.stats_owl[1]/60, 2)}h - {int(self.stats_owl[1]/60)*5} tokens \n"
            f"<p>{self.stats_owl[2]} min - {round(self.stats_owl[2]/60, 2)}h - {int(self.stats_owl[2]/60)*5} tokens \n"
        )
        stats_owc_text1 = (
            f"<p>Last 24h"
            f"<p>Last 7d"
            f"<p>This Month"
        )
        stats_owc_text2 = (
            f"<p>{self.stats_owc[0]} min - {round(self.stats_owc[0]/60, 2)}h\n"
            f"<p>{self.stats_owc[1]} min - {round(self.stats_owc[1]/60, 2)}h\n"
            f"<p>{self.stats_owc[2]} min - {round(self.stats_owc[2]/60, 2)}h\n"
        )

        btn_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        btn_box.rejected.connect(self.reject)

        innerlayout1 = QHBoxLayout()
        innerlayout1.addWidget(label_owl, alignment=Qt.AlignCenter)
        innerlayout1.addWidget(QLabel(stats_owl_text1))
        innerlayout1.addWidget(QLabel(stats_owl_text2))
        innerlayout2 = QHBoxLayout()
        innerlayout2.addWidget(label_owc, alignment=Qt.AlignCenter)
        innerlayout2.addWidget(QLabel(stats_owc_text1))
        innerlayout2.addWidget(QLabel(stats_owc_text2))
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setLineWidth(3)

        outer_layout.addLayout(innerlayout1)
        outer_layout.addWidget(line)
        outer_layout.addLayout(innerlayout2)
        outer_layout.addWidget(btn_box)

        outer_layout.setSpacing(20)

        self.setLayout(outer_layout)
        
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