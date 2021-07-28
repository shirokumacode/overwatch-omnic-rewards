from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os, json

import logging

logger = logging.getLogger(__name__)


class Settings():
    # Default settings
    settings = {
        'account': '',
        'owl': True,
        'owc': True,
        'min_check': 10
    }

    def __init__(self, location: str):
        self.file_path = location
        self.load_settings()

    def get(self, key, default=None):
        if key in self.settings:
            return self.settings[key]
        else:
            return default

    def load_settings(self):
        if not os.path.isfile(self.file_path):
            logger.info("Settings file doesn't exist.")
            return

        with open(self.file_path, 'r') as f:
            try:
                self.settings.update(json.load(f))
            except Exception as e:
                logger.error("Error loading settings file - " + str(e))
        logger.info("Settings loaded")

    def set(self, key, value, flush_file=True):
        logger.debug(f"Setting: {key} - {value}")
        if key:
            self.settings[key] = value
        if flush_file:
            self.write_file()

    def write_file(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.settings, f, sort_keys=True, indent=4)


class SettingsDialog(QDialog):
    def __init__(self, icon: QIcon, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        self.setWindowTitle("Settings")
        self.setWindowIcon(icon)

        self._setup_ui()
        self.refresh_values()
        self._connect_slots()

        self.setFixedSize(self.sizeHint())

    def _setup_ui(self):
        outer_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_1 = QWidget()
        self.tab_2 = QWidget()
        self.tab_widget.addTab(self.tab_1, "Main")
        self.tab_widget.addTab(self.tab_2, "Experimental")

        # Tab 1
        tab_1_layout = QFormLayout()
        self.account_input = QPushButton()
        self.owl_input = QCheckBox()
        self.owc_input = QCheckBox()
        tab_1_layout.addRow("Account", self.account_input)
        tab_1_layout.addRow(" ", QWidget())  # Spacer hack
        tab_1_layout.addRow("Watch OWL", self.owl_input)
        tab_1_layout.addRow("Watch OWC", self.owc_input)
        tab_1_layout.addRow(" ", QWidget())  # Spacer hack
        self.tab_1.setLayout(tab_1_layout)

        # Tab 2
        tab_2_layout = QFormLayout()
        self.min_check_input = QSpinBox()
        self.min_check_input.setMinimum(1)
        self.min_check_input.setMaximum(60)
        tab_2_layout.addRow("Check every (min)", self.min_check_input)
        self.tab_2.setLayout(tab_2_layout)

        btn_box = QDialogButtonBox(QDialogButtonBox.Close)
        btn_box.rejected.connect(self.reject)

        outer_layout.addWidget(self.tab_widget)
        outer_layout.addWidget(btn_box)

        self.setLayout(outer_layout)

    def refresh_values(self):
        if account_id := self.settings.get('account'):
            self.account_input.setText(account_id)
        else:
            self.account_input.setText("Click to add")
        self.owl_input.setChecked(self.settings.get('owl'))
        self.owc_input.setChecked(self.settings.get('owc'))
        self.min_check_input.setValue((self.settings.get('min_check')))

    def refresh_account(self):
        if account_id := self.settings.get('account'):
            self.account_input.setText(account_id)
        else:
            self.account_input.setText("Click to add")

    def _connect_slots(self):
        self.owl_input.stateChanged.connect(lambda state: self.settings.set('owl', True if state else False))
        self.owc_input.stateChanged.connect(lambda state: self.settings.set('owc', True if state else False))
        self.min_check_input.valueChanged.connect(lambda value: self.settings.set('min_check', value))


if __name__ == "__main__":
    import os
    settings = Settings('config.json')
    app = QApplication([])
    icon_owl = QIcon(os.path.join("icons", "iconowl.png"))
    dialog = SettingsDialog(icon_owl, settings)
    dialog.exec_()
