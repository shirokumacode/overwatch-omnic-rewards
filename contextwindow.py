from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os
import resources_qc

class ContextWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)

        self._create_icons()

        layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        self.status_icon = QLabel("Status_icon")
        self.status_icon.setPixmap(self.icon_disabled.pixmap(35, 35))
        top_layout.addWidget(self.status_icon, stretch=1)

        top_layout.addStretch(1)

        self.check_icon = QToolButton()
        self.check_icon.setIcon(self.icon_refresh)
        self.check_icon.setIconSize(QSize(26, 26))
        top_layout.addWidget(self.check_icon, stretch=1)

        settings_icon = QToolButton()
        settings_icon.setIconSize(QSize(26, 26))
        settings_icon.setIcon(self.icon_settings)
        settings_icon.setToolTip("Settings Dialog")
        top_layout.addWidget(settings_icon, stretch=1)
        stats_icon = QToolButton()
        stats_icon.setIcon(self.icon_stats)
        stats_icon.setIconSize(QSize(26, 26))
        top_layout.addWidget(stats_icon, stretch=1)
        shutdown_icon = QToolButton()
        shutdown_icon.setIcon(self.icon_shutdown)
        shutdown_icon.setCheckable(True)
        shutdown_icon.setIconSize(QSize(26, 26))
        top_layout.addWidget(shutdown_icon, stretch=1)
        exit_icon = QToolButton()
        exit_icon.setIcon(self.icon_exit)
        exit_icon.setIconSize(QSize(26, 26))
        top_layout.addWidget(exit_icon, stretch=1)

        self.status_text = QLabel("This is a text example of a status text with word wrap")
        self.status_text.setWordWrap(True)

        self.image_widget = QLabel("Thumbnail")
        self.image_widget.setMinimumSize(170, 135)
        self.image_widget.hide()

        self.links_stack = QStackedLayout()

        links_not_live_widget = QWidget()
        links_live_widget = QWidget()

        owl_icon1 = QLabel("OWL")
        owl_icon1.setPixmap(self.icon_owl.pixmap(35, 35))
        owc_icon1 = QLabel("OWC")
        owc_icon1.setPixmap(self.icon_owc.pixmap(35, 35))
        owl_icon2 = QLabel("OWL")
        owl_icon2.setPixmap(self.icon_owl.pixmap(35, 35))
        owc_icon2 = QLabel("OWC")
        owc_icon2.setPixmap(self.icon_owc.pixmap(35, 35))

        links_not_live_layout = QHBoxLayout()

        owl_links = QVBoxLayout()

        owl_home_button = QToolButton()
        owl_home_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owl_home_button_act = QAction()
        owl_home_button_act.setIcon(QIcon(os.path.join(":icons", "iconowl.png")))
        owl_home_button_act.setText("Home")
        owl_home_button.setDefaultAction(owl_home_button_act)
        owl_links.addWidget(owl_home_button)

        owl_schedule_button = QToolButton()
        owl_schedule_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owl_schedule_button_act = QAction()
        owl_schedule_button_act.setIcon(QIcon(os.path.join(":icons", "iconowl.png")))
        owl_schedule_button_act.setText("Schedule")
        owl_schedule_button.setDefaultAction(owl_schedule_button_act)
        owl_links.addWidget(owl_schedule_button)

        owl_youtube_button = QToolButton()
        owl_youtube_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owl_youtube_button_act = QAction()
        owl_youtube_button_act.setIcon(QIcon(os.path.join(":icons", "iconowl.png")))
        owl_youtube_button_act.setText("Youtube Ch")
        owl_youtube_button.setDefaultAction(owl_youtube_button_act)
        owl_links.addWidget(owl_youtube_button)

        owc_links = QVBoxLayout()

        owc_home_button = QToolButton()
        owc_home_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owc_home_button_act = QAction()
        owc_home_button_act.setIcon(QIcon(os.path.join(":icons", "iconowc.png")))
        owc_home_button_act.setText("Home")
        owc_home_button.setDefaultAction(owc_home_button_act)
        owc_links.addWidget(owc_home_button)

        owc_schedule_button = QToolButton()
        owc_schedule_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owc_schedule_button_act = QAction()
        owc_schedule_button_act.setIcon(QIcon(os.path.join(":icons", "iconowc.png")))
        owc_schedule_button_act.setText("Schedule")
        owc_schedule_button.setDefaultAction(owc_schedule_button_act)
        owc_links.addWidget(owc_schedule_button)

        owc_youtube_button = QToolButton()
        owc_youtube_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owc_youtube_button_act = QAction()
        owc_youtube_button_act.setIcon(QIcon(os.path.join(":icons", "iconowc.png")))
        owc_youtube_button_act.setText("Youtube Ch")
        owc_youtube_button.setDefaultAction(owc_youtube_button_act)
        owc_links.addWidget(owc_youtube_button)

        #links_not_live_layout.addWidget(owl_icon1, stretch=1)
        links_not_live_layout.addLayout(owl_links, stretch=4)
        #links_not_live_layout.addStretch(2)
        #links_not_live_layout.addWidget(owc_icon1, stretch=1)
        links_not_live_layout.addLayout(owc_links, stretch=4)

        links_live_layout = QHBoxLayout()

        owl_links = QVBoxLayout()

        owl_weblive_button = QToolButton()
        owl_weblive_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owl_weblive_button_act = QAction()
        owl_weblive_button_act.setIcon(QIcon(os.path.join(":icons", "iconowl.png")))
        owl_weblive_button_act.setText("OWL Website")
        owl_weblive_button.setDefaultAction(owl_weblive_button_act)
        owl_links.addWidget(owl_weblive_button)

        owl_ytlive_button = QToolButton()
        owl_ytlive_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owl_ytlive_button_act = QAction()
        owl_ytlive_button_act.setIcon(QIcon(os.path.join(":icons", "iconowl.png")))
        owl_ytlive_button_act.setText("Youtube Live")
        owl_ytlive_button.setDefaultAction(owl_ytlive_button_act)
        owl_links.addWidget(owl_ytlive_button)

        owc_links = QVBoxLayout()

        owc_weblive_button = QToolButton()
        owc_weblive_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owc_weblive_button_act = QAction()
        owc_weblive_button_act.setIcon(QIcon(os.path.join(":icons", "iconowc.png")))
        owc_weblive_button_act.setText("OWC Website")
        owc_weblive_button.setDefaultAction(owc_weblive_button_act)
        owc_links.addWidget(owc_weblive_button)

        owc_ytlive_button = QToolButton()
        owc_ytlive_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        owc_ytlive_button_act = QAction()
        owc_ytlive_button_act.setIcon(QIcon(os.path.join(":icons", "iconowc.png")))
        owc_ytlive_button_act.setText("Youtube Live")
        owc_ytlive_button.setDefaultAction(owc_ytlive_button_act)
        owc_links.addWidget(owc_ytlive_button)

        #links_live_layout.addWidget(owl_icon2, stretch=1)
        links_live_layout.addLayout(owl_links, stretch=4)
        #links_live_layout.addStretch(2)
        #links_live_layout.addWidget(owc_icon2, stretch=1)
        links_live_layout.addLayout(owc_links, stretch=4)

        links_not_live_widget.setLayout(links_not_live_layout)
        links_live_widget.setLayout(links_live_layout)

        self.links_stack.addWidget(links_not_live_widget)
        self.links_stack.addWidget(links_live_widget)


        layout.addLayout(top_layout, stretch=2)
        layout.addWidget(self.status_text, stretch=2, alignment=Qt.AlignRight)
        layout.addWidget(self.image_widget, stretch=8, alignment=Qt.AlignHCenter)
        layout.addLayout(self.links_stack, stretch=2)

        self.links_stack.setCurrentIndex(2)
        self.setLayout(layout)

    def showPanel(self):
        position = QCursor.pos()
        self.setGeometry(position.x(), position.y(), 300, 300)  # arbitrary size/location
        self.show()
        self.raise_()
        self.setFocus()

    def closePanel(self):
        self.hide()
        self.close()

    def focusOutEvent(self, e: QFocusEvent) -> None:
        self.closePanel()

    def _create_icons(self):
        self.icon_disabled = QIcon(os.path.join(":icons", "icondisabled.png"))
        self.icon_owl = QIcon(os.path.join(":icons", "iconowl.png"))
        self.icon_owc = QIcon(os.path.join(":icons", "iconowc.png"))
        self.icon_error = QIcon(os.path.join(":icons", "iconerror.png"))
        self.icon_error = QIcon(os.path.join(":icons", "iconerror.png"))
        self.icon_settings = QIcon(os.path.join(":icons", "settings.png"))
        self.icon_stats = QIcon(os.path.join(":icons", "stats.png"))
        self.icon_shutdown = QIcon(os.path.join(":icons", "shutdown.png"))
        self.icon_exit = QIcon(os.path.join(":icons", "exit.png"))
        self.icon_home = QIcon(os.path.join(":icons", "home.png"))
        self.icon_schedule = QIcon(os.path.join(":icons", "schedule.png"))
        self.icon_youtube = QIcon(os.path.join(":icons", "youtube.png"))
        self.icon_refresh = QIcon(os.path.join(":icons", "refresh.png"))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = ContextWindow()
    window.showPanel()
    print(window.geometry())

    app.exec_()