from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import logging
import os
import platform
import sys

from accountdialog import AccountDialog
from checkviewer import CheckViewer
from settings import SettingsManager, SettingsDialog, Actions, Urls
from stats import Stats, StatsDialog

import resources_qc

logger = logging.getLogger(__name__)


class SystemTray(QSystemTrayIcon):
    exit_signal = pyqtSignal(bool)

    def __init__(self, settings: SettingsManager, stats: Stats, quiet_mode=False, parent=None):
        super().__init__(parent)
        logger.info("Starting system tray")

        self.create_icons()
        self.setIcon(self.icon_disabled)
        QApplication.instance().setWindowIcon(self.icon_owl)

        self.settings = settings
        self.stats = stats
        self.shutdown_flag = False

        self.create_menu()
        self.activated.connect(self.click_systray)

        self.create_thread()

        self.settings_dialog = SettingsDialog(self.icon_owl, self.settings)
        self.settings_dialog.account_input.clicked.connect(self.account_setup)
        self.settings_dialog.owl_input.stateChanged.connect(self.check_viewer.set_owl_flag)
        self.settings_dialog.owc_input.stateChanged.connect(self.check_viewer.set_owc_flag)
        self.settings_dialog.min_check_input.valueChanged.connect(self.check_viewer.set_min_check)
        self.settings_dialog.force_track.stateChanged.connect(self.check_viewer.set_force_rewards)

        self.stats_dialog = StatsDialog(self.stats, self.icon_owl, self.icon_owc)

        if not self.settings.get("account"):
            self.setIcon(self.icon_error)
            logger.error("Account not set")
            self.status_action.setText(f"Status: No account setup")
            self.showMessage("Account Not Set", "Setup an account to begin watching", self.icon_error, 5000)
            self.checknow_action.setVisible(False)
            self.shutdown_action.setVisible(False)
        else:
            self.account_action.setText(f"Account: {self.settings.get('account')}")

        if not quiet_mode:
            self.setVisible(True)

    def create_icons(self):
        # Create the icons
        self.icon_disabled = QIcon(os.path.join(":icons", "icondisabled.png"))
        self.icon_owl = QIcon(os.path.join(":icons", "iconowl.png"))
        self.icon_owc = QIcon(os.path.join(":icons", "iconowc.png"))
        self.icon_error = QIcon(os.path.join(":icons", "iconerror.png"))

    def create_menu(self):
        self.menu = QMenu()

        self.status_action = QAction("Status: Initializing")
        self.status_action.setEnabled(False)

        self.account_action = QAction("Account: Click to set up")

        self.checknow_action = QAction("Check now")

        self.shutdown_action = QAction("Shutdown on end")
        self.shutdown_action.setCheckable(True)

        self.stats_action = QAction("Stats/History")
        self.settings_action = QAction("Settings")
        self.quit_action = QAction("Exit")

        self.menu.addAction(self.status_action)
        self.menu.addSeparator()
        self.menu.addAction(self.account_action)
        self.menu.addSeparator()
        self.menu.addAction(self.checknow_action)
        self.menu.addAction(self.shutdown_action)
        self.menu.addSeparator()
        self.menu.addAction(self.stats_action)
        self.menu.addAction(self.settings_action)

        self.menu.addAction(self.quit_action)

        self.account_action.triggered.connect(self.account_setup)
        self.stats_action.triggered.connect(self.show_stats)
        self.settings_action.triggered.connect(self.show_settings)
        self.quit_action.triggered.connect(lambda: QApplication.instance().quit())

        self.setToolTip("Overwatch Omnic Perks")
        self.setContextMenu(self.menu)

    def create_thread(self):
        logger.info("Creating thread")

        self.thread = QThread()

        self.check_viewer = CheckViewer(
            self.settings.get('account'),
            owl_flag=self.settings.get('owl'),
            owc_flag=self.settings.get('owc'),
            min_check=self.settings.get('min_check')
        )
        self.check_viewer.moveToThread(self.thread)

        self.thread.started.connect(self.check_viewer.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.check_viewer.check_progress.connect(self.update_check_progress)
        self.check_viewer.checking.connect(self.update_check_progress)
        self.check_viewer.watching_owl.connect(self.update_watching_owl)
        self.check_viewer.watching_owc.connect(self.update_watching_owc)
        self.check_viewer.false_tracking.connect(self.update_false_tracking)
        self.check_viewer.error.connect(self.update_error)
        self.check_viewer.exit_signal.connect(self.check_viewer.deleteLater)

        self.checknow_action.triggered.connect(self.check_viewer.start_check_timer)
        self.exit_signal.connect(self.check_viewer.prepare_to_exit)

        self.thread.start()

    @pyqtSlot(str, bool)
    def update_error(self, error_msg, notification):
        self.setIcon(self.icon_error)
        self.checknow_action.setEnabled(True)
        self.status_action.setText(f"Status: {error_msg}")
        self.stats.write_record()
        if notification:
            self.showMessage(
                "Error - OWL Omnic Rewards",
                f"{error_msg} \n Perform a check now or restart app",
                self.icon_error, 10000)

    @pyqtSlot()
    @pyqtSlot(int)
    def update_check_progress(self, min_remaining=None):
        self.setIcon(self.icon_disabled)
        if min_remaining:
            logger.info(f"Not Live - {min_remaining}min until next check")
            self.status_action.setText(f"Status: Not Live - {min_remaining}min until next check")
            self.checknow_action.setEnabled(True)
            if self.shutdown_flag and min_remaining == self.settings.get('min_check'):
                if self.shutdown_action.isChecked():
                    logger.info("Shutdown in 30s")
                    self.showMessage("Shutdown in 30s",
                                     "Not Live. Will try to shutdown in 30s. Uncheck the option to cancel",
                                     self.icon_owl, 30000)
                    QTimer.singleShot(30000, self.shutdown_computer)
                else:
                    self.shutdown_flag = False
        else:
            logger.info("Checking OWL/OWC page")
            self.status_action.setText("Status: Checking OWL/OWC page")

    @pyqtSlot(int, str, bool)
    def update_watching_owl(self, min_watching, title, end):
        self.setIcon(self.icon_owl)
        self.stats.set_record(False, min_watching, title, self.settings.get('account'))
        if not end:
            if min_watching == 0:
                self.showMessage("Watching Overwatch League", title, self.icon_owl, 10000)
                self.checknow_action.setEnabled(False)
                logger.info("Started watching OWL")
            self.status_action.setText(f"Status: Watching OWL for {min_watching}min")
            logger.info(f"Watching OWL for {min_watching}min")
        else:
            self.stats.write_record()
            self.showMessage("Watched Overwatch League",
                             f"Watched {min_watching}mins of {title}",
                             self.icon_owl, 10000)
            logger.info(f"Watched {min_watching}mins of OWL - {title}")

            self.status_action.setText(f"Status: Watched OWL for {min_watching}min")
            self.checknow_action.setEnabled(True)
            if self.shutdown_action.isChecked():
                self.shutdown_flag = True

    @pyqtSlot(int, str, bool)
    def update_watching_owc(self, min_watching, title, end):
        self.setIcon(self.icon_owc)
        self.stats.set_record(True, min_watching, title, self.settings.get('account'))
        if not end:
            if min_watching == 0:
                self.showMessage("Watching Overwatch Contenders", title, self.icon_owc, 10000)
                self.checknow_action.setEnabled(False)
                logger.info("Started watching OWC")
            self.status_action.setText(f"Status: Watching OWC for {min_watching}min")
            logger.info(f"Watching OWC for {min_watching}min")
        else:
            self.stats.write_record()
            self.showMessage("Watched Overwatch Contenders",
                             f"Watched {min_watching}mins of {title}",
                             self.icon_owc,
                             10000)
            logger.info(f"Watched {min_watching}mins of OWC - {title}")

            self.status_action.setText(f"Status: Watched OWC for {min_watching}min")
            self.checknow_action.setEnabled(True)
            if self.shutdown_action.isChecked():
                self.shutdown_flag = True

    @pyqtSlot(bool)
    def update_false_tracking(self, contenders):
        self.setIcon(self.icon_error)
        if contenders:
            self.status_action.setText("Status: OWC seems Live, not tracking")
        else:
            self.status_action.setText("Status: OWL seems Live, not tracking")

    @pyqtSlot()
    def account_setup(self):
        logger.info("Opening account dialog")
        self.account_dialog = AccountDialog(self.icon_owl)
        self.account_dialog.accepted.connect(self.save_account)
        self.account_dialog.show()
        self.account_dialog.raise_()
        self.account_dialog.activateWindow()

    @pyqtSlot()
    def save_account(self):
        logger.info("Setting account")
        account_id = self.account_dialog.get_userid()
        self.settings.set(key='account', value=account_id)
        self.stats.write_record()
        QMetaObject.invokeMethod(
            self.check_viewer,
            'set_userid',
            Q_ARG(str, account_id)
        )
        self.checknow_action.setVisible(True)
        self.shutdown_action.setVisible(True)
        self.account_dialog.deleteLater()

        self.account_action.setText(f"Account: {self.settings.get('account')}")
        self.settings_dialog.refresh_account()

    @pyqtSlot()
    def show_stats(self):
        self.stats_dialog.show_dialog(self.settings.get('account'))

    @pyqtSlot()
    def show_settings(self):
        logger.info("Opening settings dialog")
        # Debug current widgets (useful for memory leaks
        #print(list(filter(lambda x: isinstance(x, SettingsDialog), QApplication.allWidgets())))

        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
        # Make sure settings dialog is not deleted
        # self.settings_dialog.finished.connect(self.settings_dialog.deleteLater)

    @pyqtSlot()
    def prepare_to_exit(self):
        logger.info("Preparing to exit")
        self.stats.write_record()
        self.exit_signal.emit(True)
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

    def shutdown_computer(self):
        if self.shutdown_action.isChecked():
            logger.info("Shutting down computer")
            system = platform.system()
            if system == 'Linux':
                os.system("systemctl poweroff")
            elif system == 'Windows':
                os.system("shutdown /s /f /t 30")
            elif system == 'Darwin':
                os.system("osascript -e tell app \"Finder\" to shut down")
        else:
            logger.info("Shutdown was canceled")
            self.shutdown_flag = False

    def click_systray(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            action = self.settings.get('left_click')
            self.perform_action(action)
        elif reason == QSystemTrayIcon.MiddleClick:
            action = self.settings.get('middle_click')
            self.perform_action(action)

    def perform_action(self, action):
        # Needs rewrite under Python 3.10 using match - Pattern Matching
        if action is None:
            return
        elif action == Actions.context_menu:
            self.contextMenu().popup(QCursor.pos())
        elif action == Actions.open_youtube:
            record = self.stats.get_record()
            if record is None:
                QDesktopServices.openUrl(QUrl(Urls.owl.youtube_channel))
            elif not record.contenders:
                QDesktopServices.openUrl(QUrl(Urls.owl.youtube_live))
            elif record.contenders:
                QDesktopServices.openUrl(QUrl(Urls.owc.youtube_live))
        elif action == Actions.open_owl_owc:
            record = self.stats.get_record()
            if record is None:
                QDesktopServices.openUrl(QUrl(Urls.owl.main))
            elif not record.contenders:
                QDesktopServices.openUrl(QUrl(Urls.owl.main))
            elif record.contenders:
                QDesktopServices.openUrl(QUrl(Urls.owc.main))
        elif action == Actions.test_action:
            self.showMessage("Example", "test")
        else:
            logger.warning(f'Unknown action - {action}')
