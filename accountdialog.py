from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class AccountDialog(QDialog):

    def __init__(self, icon, parent=None):
        super().__init__(parent)

        self.setWindowIcon(icon)

        self.userID = ""

        self.setWindowTitle("Account Setup")

        outer_layout = QVBoxLayout()

        blizzard_url = "<a href=\"https://www.blizzard.com\">blizzard.com</a>"
        blizzard_user_url = "<a href=\"https://www.blizzard.com/navbar/authenticate\">blizzard.com/navbar/authenticate</a>"

        instructions_text = (
            f"<h3 style=\"text-align:center\">How to get your Blizzard user ID</h3>\n"
            f"<p>1 - <b>Go to</b> {blizzard_url}\n"
            f"<p>2 - <b>Login</b> into your account\n"
            f"<p>3 - <b>While logged in</b>, go to {blizzard_user_url}\n"
            f"<p>4 - <b>Copy</b> the id field\n"
            f"<p>5 - <b>Paste</b> the number below\n"
        )

        instructions_label = QLabel(instructions_text)
        instructions_label.setTextFormat(Qt.RichText)
        instructions_label.setOpenExternalLinks(True)

        form_layout = QFormLayout()
        self.userid_input = QLineEdit()
        self.userid_input.maxLength = 15
        self.userid_input.setValidator(QRegularExpressionValidator(QRegularExpression(r"\s*[0-9]+\s*")))
        form_layout.addRow("UserId", self.userid_input)

        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.process_value)
        btn_box.rejected.connect(self.reject)

        outer_layout.addWidget(instructions_label)
        outer_layout.addLayout(form_layout)
        outer_layout.addWidget(btn_box)

        outer_layout.setSpacing(20)

        self.setLayout(outer_layout)

        self.setFixedSize(self.sizeHint())

    def process_value(self):
        self.userID = self.userid_input.text().strip()
        self.accept()

    def get_userid(self):
        return self.userID


if __name__ == "__main__":
    import os

    app = QApplication([])
    icon_owl = QIcon(os.path.join("icons", "iconowl.png"))
    dialog = AccountDialog(icon_owl)
    dialog.exec_()
    print(dialog.get_userid())
