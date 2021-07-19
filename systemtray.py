from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os, sys, json, platform, csv, io
from datetime import datetime, timezone

from checkviewer import CheckViewer
from accountdialog import AccountDialog
from stats import Stats
from settings import Settings

import resources_qc

import logging
logger = logging.getLogger(__name__)

class SystemTray(QSystemTrayIcon):
    owl_flag_signal = pyqtSignal(bool)
    owc_flag_signal = pyqtSignal(bool)
    exit_signal = pyqtSignal(bool)

    def __init__(self, quiet_mode=False, parent=None):
        super().__init__(parent=parent)
        logger.info("Starting system tray")

        # PyInstaller fix for application path
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        self.config_location = os.path.join(application_path, 'config.json')
        self.history_location = os.path.join(application_path, 'history.csv')

        self.settings = Settings(self.config_location)
        self.stats = Stats(self.history_location)
        self.shutdown_flag = False
        self.thread = None

        self.create_icons()
        self.setIcon(self.icon_disabled)
        QApplication.instance().setWindowIcon(self.icon_owl)

        self.create_menu()
        self.activated.connect(self.click_systray)

        if not quiet_mode:
            self.setVisible(True)

        if self.settings.get("account"):
            self.create_thread()
        else:
            self.setIcon(self.icon_error)
            logger.error("Account not set")
            self.status_action.setText(f"Status: No account setup")
            self.showMessage("Account Not Set", "Setup an account to begin watching", self.icon_error, 5000)

    def click_systray(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.contextMenu().popup((QCursor.pos()))
        elif reason == QSystemTrayIcon.MiddleClick:
            # TODO Open Stream URL (Youtube or OWL/OWC) 
            # QDesktopServices.openUrl()
            pass

    def create_icons(self):    
        # Create the icons
        self.icon_disabled = QIcon(os.path.join(":icons","icondisabled.png"))
        self.icon_owl = QIcon(os.path.join(":icons", "iconowl.png"))
        self.icon_owc = QIcon(os.path.join(":icons", "iconowc.png"))
        self.icon_error = QIcon(os.path.join(":icons", "iconerror.png"))

    def create_menu(self):
        self.menu = QMenu()

        self.status_action = QAction("Status: Initializing")
        self.status_action.setEnabled(False)

        self.account_action = QAction("Account: Click to set up")

        self.checknow_action = QAction("Check now")
        self.checknow_action.setVisible(False)

        self.owl_checker_action = QAction("OWL")
        self.owl_checker_action.setVisible(False)
        self.owl_checker_action.setCheckable(True)
        self.owl_checker_action.setChecked(self.settings.get('owl', default=True))

        self.owc_checker_action = QAction("OWC")
        self.owc_checker_action.setCheckable(True)
        self.owc_checker_action.setVisible(False)
        self.owc_checker_action.setChecked(self.settings.get('owc', default=True))

        self.shutdown_action = QAction("Shutdown after end (Beta)")
        self.shutdown_action.setCheckable(True)
        self.shutdown_action.setVisible(False)
        
        self.stats_action = QAction("Stats/History")
        self.quit_action= QAction("Exit")
    
        self.menu.addAction(self.status_action)
        self.menu.addSeparator()
        self.menu.addAction(self.account_action)
        self.menu.addSeparator()
        self.menu.addAction(self.checknow_action)
        self.menu.addAction(self.owl_checker_action)
        self.menu.addAction(self.owc_checker_action)
        self.menu.addAction(self.shutdown_action)
        self.menu.addSeparator()
        self.menu.addAction(self.stats_action)
        self.menu.addAction(self.quit_action)

        self.account_action.triggered.connect(self.account_setup)
        self.owl_checker_action.triggered.connect(self.set_owl_flag)
        self.owc_checker_action.triggered.connect(self.set_owc_flag)
        self.stats_action.triggered.connect(self.show_stats)
        self.quit_action.triggered.connect(lambda : QApplication.instance().quit())

        self.setToolTip("Overwatch Omnic Perks")
        self.setContextMenu(self.menu)

    def create_thread(self):
        logger.info("Creating thread")
        self.account_action.setText(f"Account: {self.settings.get('account')}")

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
        self.owl_flag_signal.connect(self.check_viewer.set_owl_flag)
        self.owc_flag_signal.connect(self.check_viewer.set_owc_flag)
        self.exit_signal.connect(self.check_viewer.prepare_to_exit)
        
        self.thread.start()

        self.checknow_action.setVisible(True)
        self.owl_checker_action.setVisible(True)
        self.owc_checker_action.setVisible(True)
        self.shutdown_action.setVisible(True)

    @pyqtSlot(str, bool)
    def update_error(self, error_msg, notification):
        self.setIcon(self.icon_error)
        self.checknow_action.setEnabled(True)
        self.status_action.setText(f"Status: {error_msg}")
        self.stats.write_record()
        if notification:
            self.showMessage("Error - OWL Omnic Rewards", f"{error_msg} \n Perform a check now or restart app", self.icon_error, 10000)

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
                    self.showMessage("Shutdown in 30s", "Not Live. Will try to shutdown in 30s. Uncheck the option to cancel", self.icon_owl, 30000)
                    QTimer.singleShot(30000, self.shutdown_computer)
                else:
                     self.shutdown_flag = False
        else:
            logger.info("Checking OWL/OWC page")
            self.status_action.setText("Status: Checking OWL/OWC page")

    @pyqtSlot(int,str,bool)
    def update_watching_owl(self, min_watching, title, end):
        self.setIcon(self.icon_owl)
        self.stats.set_record(False, min_watching, title, self.settings.get('account'))
        if min_watching == 0:
            self.showMessage("Watching Overwatch League", title, self.icon_owl, 10000)
            self.checknow_action.setEnabled(False)
            logger.info("Started watching OWL")
        if not end:
            self.status_action.setText(f"Status: Watching OWL for {min_watching}min")
            logger.info(f"Watching OWL for {min_watching}min")
        else:
            self.stats.write_record()
            self.showMessage("Watched Overwatch League", f"Watched {min_watching}mins of {title}", self.icon_owl, 10000)
            logger.info(f"Watched {min_watching}mins of OWL - {title}")

            self.status_action.setText(f"Status: Watched OWL for {min_watching}min")
            self.checknow_action.setEnabled(True)
            if self.shutdown_action.isChecked():
                self.shutdown_flag = True 

    @pyqtSlot(int,str,bool)
    def update_watching_owc(self, min_watching, title, end):
        self.setIcon(self.icon_owc)
        self.stats.set_record(True, min_watching, title, self.settings.get('account'))
        if min_watching == 0:
            self.showMessage("Watching Overwatch Contenders", title, self.icon_owc, 10000)
            self.checknow_action.setEnabled(False)
            logger.info("Started watching OWC")
        if not end:
            self.status_action.setText(f"Status: Watching OWC for {min_watching}min")
            logger.info(f"Watching OWC for {min_watching}min")
        else:
            self.stats.write_record()
            self.showMessage("Watched Overwatch Contenders", f"Watched {min_watching}mins of {title}", self.icon_owc, 10000)
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
        logger.info("Open setting account")
        account_dialog = AccountDialog(self.icon_owl)
        if account_dialog.exec_():
            logger.info("Setting account id")
            self.settings.set(key='account', value=account_dialog.get_userid())
            if self.thread:
                self.thread.quit()
                self.thread.wait()
            self.stats.write_record()
            self.create_thread()
        account_dialog.deleteLater()
        logger.info("Closed Setting account")
    
    @pyqtSlot(bool)
    def set_owl_flag(self, checked):
        self.settings.set('owl', checked)
        self.owl_flag_signal.emit(checked)
    
    @pyqtSlot(bool)
    def set_owc_flag(self, checked):
        self.settings.set('owc', checked)
        self.owc_flag_signal.emit(checked)


    @pyqtSlot()
    def show_stats(self):
        self.stats.show(self.icon_owl, self.icon_owc, self.settings.get('account'))

    @pyqtSlot()
    def prepare_to_exit(self):
        logger.info("Preparing to exit")
        self.stats.write_record()
        if self.thread: 
            self.exit_signal.emit(True)
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

    

