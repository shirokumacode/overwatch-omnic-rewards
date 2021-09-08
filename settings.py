from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

import json
from json import JSONDecodeError
import dataclasses
from dataclasses import dataclass
from typing import Optional

import os

import logging
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Urls:
    @dataclass()
    class UrlsBase:
        main: str
        schedule: str
        youtube_channel: str
        youtube_live: str

    owl = UrlsBase(
        main="https://overwatchleague.com",
        schedule="https://overwatchleague.com/schedule",
        youtube_channel="https://youtube.com/overwatchleague",
        youtube_live="https://youtube.com/overwatchleague/live"
    )
    owc = UrlsBase(
        main="https://overwatchcontenders.com",
        schedule="https://overwatchcontenders.com/schedule",
        youtube_channel="https://youtube.com/overwatchcontenders",
        youtube_live="https://youtube.com/overwatchcontenders/live"
    )


class Actions:
    """ Helper static class to improve code readability when using Actions (decode string).
    Works as a enum (but not one)"""
    nothing = None
    context_menu = 'context_menu'
    test_action = 'test'
    open_youtube = 'open_youtube'
    open_owl_owc = 'open_owl_owc'

    @classmethod
    def actions(cls):
        return [cls.context_menu, cls.test_action, cls.open_youtube, cls.open_owl_owc]

    @classmethod
    def possible_actions(cls):
        return [cls.nothing, cls.context_menu, cls.test_action, cls.open_youtube, cls.open_owl_owc]


@dataclass
class Settings:
    """ Default settings class """
    account: str = ''
    owl: bool = True
    owc: bool = True
    min_check: int = 10
    middle_click: Optional[str] = Actions.open_owl_owc
    left_click: Optional[str] = Actions.context_menu

    def __post_init__(self):
        possible_actions = Actions.possible_actions()
        if self.middle_click not in possible_actions:
            self.middle_click = None
        if self.left_click not in possible_actions:
            self.left_click = None


class SettingsManager:
    # Default settings
    settings = Settings()

    def __init__(self, location: str):
        self.file_path = location
        self.load_settings()

    def get(self, key: str, default=None):
        try:
            return self.settings.__getattribute__(key)
        except AttributeError:
            return default

    def load_settings(self):
        if not os.path.isfile(self.file_path):
            logger.info("Settings file doesn't exist.")
            return

        with open(self.file_path, 'r') as f:
            try:
                data = json.load(f)
            except JSONDecodeError as e:
                logger.error("Error loading settings file - " + str(e))
                return
            # Filter extra fields
            fields = Settings.__annotations__
            data_filtered = {key: value for (key, value) in data.items() if key in fields}
            # Update fields
            for key in fields:
                if key in data_filtered:
                    self.settings.__setattr__(key, data_filtered[key])

        logger.info("Settings loaded")

    def set(self, key: str, value, flush_file=True):
        logger.debug(f"Setting: {key} - {value}")
        if key:
            self.settings.__setattr__(key, value)
        if flush_file:
            self.write_file()

    def write_file(self):
        with open(self.file_path, 'w') as f:
            json.dump(dataclasses.asdict(self.settings), f, indent=4)


class SettingsDialog(QDialog):
    def __init__(self, icon: QIcon, settings: SettingsManager, parent=None):
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

        self.left_click_input = self._create_action_combobox()
        self.middle_click_input = self._create_action_combobox()
        layout = QFormLayout()
        layout.addRow("Left Click", self.left_click_input)
        layout.addRow("Middle Click", self.middle_click_input)
        groupbox = QGroupBox()
        groupbox.setTitle("System tray Icon")
        groupbox.setLayout(layout)

        tab_1_layout.addRow("Account", self.account_input)
        tab_1_layout.addRow(" ", QWidget())  # Spacer hack
        tab_1_layout.addRow("Watch OWL", self.owl_input)
        tab_1_layout.addRow("Watch OWC", self.owc_input)
        tab_1_layout.addRow(" ", QWidget())  # Spacer hack
        tab_1_layout.addRow(groupbox)

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

    def _create_action_combobox(self):
        combo = QComboBox()
        combo.addItem("Nothing", Actions.nothing)
        combo.addItem("Context Menu", Actions.context_menu)
        combo.addItem("Open OWL/OWC website", Actions.open_owl_owc)
        combo.addItem("Open Youtube", Actions.open_youtube)
        return combo

    def refresh_values(self):
        self.refresh_account()
        self.owl_input.setChecked(self.settings.get('owl'))
        self.owc_input.setChecked(self.settings.get('owc'))
        self.min_check_input.setValue((self.settings.get('min_check')))
        self.left_click_input.setCurrentIndex(self.left_click_input.findData(self.settings.get("left_click")))
        self.middle_click_input.setCurrentIndex(self.middle_click_input.findData(self.settings.get("middle_click")))

    def refresh_account(self):
        if account_id := self.settings.get('account'):
            self.account_input.setText(account_id)
        else:
            self.account_input.setText("Click to add")
        self.account_input.adjustSize()

    def _connect_slots(self):
        self.owl_input.stateChanged.connect(lambda state: self.settings.set('owl', True if state else False))
        self.owc_input.stateChanged.connect(lambda state: self.settings.set('owc', True if state else False))
        self.min_check_input.valueChanged.connect(lambda value: self.settings.set('min_check', value))
        self.left_click_input.activated.connect(lambda index: self.settings.set('left_click', self.left_click_input.itemData(index)))
        self.middle_click_input.activated.connect(lambda index: self.settings.set('middle_click', self.middle_click_input.itemData(index)))


if __name__ == "__main__":
    import os
    settings = SettingsManager('config.json')
    app = QApplication([])
    icon_owl = QIcon(os.path.join("icons", "iconowl.png"))
    dialog = SettingsDialog(icon_owl, settings)
    print(Urls.owl.main)
    dialog.exec_()
