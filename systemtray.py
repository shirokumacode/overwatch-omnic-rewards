from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os, sys, json, platform, csv, io
from datetime import datetime, timezone

from checkviewer import CheckViewer
from accountdialog import AccountDialog
from statsdialog import StatsDialog

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

        self.settings = {'account': '', 'owl': True, 'owc': True, 'min_check': 10}
        self.shutdown_flag = False
        self.last_record = ()
        self.load_settings()
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
        if owl_flag := self.settings.get("owl"):
            self.owl_checker_action.setChecked(owl_flag)

        self.owc_checker_action = QAction("OWC")
        self.owc_checker_action.setCheckable(True)
        self.owc_checker_action.setVisible(False)
        if owc_flag := self.settings.get("owc"):
            self.owc_checker_action.setChecked(owc_flag)

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
        self.account_action.setText(f"Account: {self.settings['account']}")

        self.thread = QThread()

        self.check_viewer = CheckViewer(
                                self.settings['account'], 
                                owl_flag=self.settings['owl'], 
                                owc_flag=self.settings['owc'], 
                                min_check=self.settings['min_check'])
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
        if self.last_record:
                self.write_last_record()
        if notification:
            self.showMessage("Error - OWL Omnic Rewards", f"{error_msg} \n Perform a check now or restart app", self.icon_error, 10000)

    @pyqtSlot()
    @pyqtSlot(int)
    def update_check_progress(self, min_remaining=None):
        self.last_record = ()
        self.setIcon(self.icon_disabled)
        if min_remaining:
            logger.info(f"Not Live - {min_remaining}min until next check")
            self.status_action.setText(f"Status: Not Live - {min_remaining}min until next check")
            self.checknow_action.setEnabled(True)
            if self.shutdown_flag and min_remaining == self.settings['min_check']:
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
        if min_watching == 0:
            self.showMessage("Watching Overwatch League", title, self.icon_owl, 10000)
            self.checknow_action.setEnabled(False)
            logger.info("Started watching OWL")
        if not end:
            self.status_action.setText(f"Status: Watching OWL for {min_watching}min")
            logger.info(f"Watching OWL for {min_watching}min")
            self.last_record = (False, title, min_watching, self.settings['account'])
        else:
            self.last_record = ()
            self.showMessage("Watched Overwatch League", f"Watched {min_watching}mins of {title}", self.icon_owl, 10000)
            logger.info(f"Watched {min_watching}mins of OWL - {title}")
            self.write_watch_history(contenders=False, min_watched=min_watching, title=title)

            self.status_action.setText(f"Status: Watched OWL for {min_watching}min")
            self.checknow_action.setEnabled(True)
            if self.shutdown_action.isChecked():
                self.shutdown_flag = True 

    @pyqtSlot(int,str,bool)
    def update_watching_owc(self, min_watching, title, end):
        self.setIcon(self.icon_owc)
        if min_watching == 0:
            self.showMessage("Watching Overwatch Contenders", title, self.icon_owc, 10000)
            self.checknow_action.setEnabled(False)
            logger.info("Started watching OWC")
        if not end:
            self.status_action.setText(f"Status: Watching OWC for {min_watching}min")
            logger.info(f"Watching OWC for {min_watching}min")
            self.last_record = (True, title, min_watching, self.settings['account'])
        else:
            self.last_record = ()
            self.showMessage("Watched Overwatch Contenders", f"Watched {min_watching}mins of {title}", self.icon_owc, 10000)
            logger.info(f"Watched {min_watching}mins of OWC - {title}")
            self.write_watch_history(contenders=True, min_watched=min_watching, title=title)

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
            self.set_write_settings(key='account', value=account_dialog.get_userid())
            if self.thread:
                self.thread.quit()
                self.thread.wait()
            if self.last_record:
                self.write_last_record()
            self.create_thread()
        account_dialog.deleteLater()
        logger.info("Closed Setting account")
    
    @pyqtSlot(bool)
    def set_owl_flag(self, checked):
        self.set_write_settings('owl', checked)
        self.owl_flag_signal.emit(checked)
    
    @pyqtSlot(bool)
    def set_owc_flag(self, checked):
        self.set_write_settings('owc', checked)
        self.owc_flag_signal.emit(checked)

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

    @pyqtSlot()
    def show_stats(self):
        logger.info("Show stats")
        if not os.path.isfile(self.history_location):
            logger.warning("No history file")
            history_data = {}
            self.stats_dialog = StatsDialog(history_data, self.settings['account'], self.icon_owl, self.icon_owc)
            self.stats_dialog.show()
        else:
            with open(self.history_location, 'r', newline='') as history_file:
                history_data = csv.DictReader(history_file)
                logger.info("Loaded history file")
                self.stats_dialog = StatsDialog(history_data, self.settings['account'], self.icon_owl, self.icon_owc)
                self.stats_dialog.show()
                self.stats_dialog.raise_()
                self.stats_dialog.activateWindow()
        self.stats_dialog.finished.connect(self.stats_dialog.deleteLater)

    @pyqtSlot()
    def prepare_to_exit(self):
        logger.info("Preparing to exit")
        if self.last_record:
                self.write_last_record()
        if self.thread: 
            self.exit_signal.emit(True)
            self.thread.quit()
            self.thread.wait()

    def load_settings(self):
        if not os.path.isfile(self.config_location):
            logger.info("Settings file doesn't exist.")
            return

        with open(self.config_location, 'r') as f:
            try:
                self.settings.update(json.load(f))
            except Exception as e:
                logger.error("Error loading settings file - " + str(e))
        logger.info("Settings loaded")
    
    def set_write_settings(self, key=None, value=None):
        logger.info(f"Setting: {key} - {value}")
        if key:
            self.settings[key] = value
        with open(self.config_location, 'w') as f:
            json.dump(self.settings, f, sort_keys=True, indent=4)
    
    def write_last_record(self):
        contenders, title, min_watch, accountid = self.last_record
        self.write_watch_history(contenders, min_watch, title, accountid)
        self.last_record = ()

    def write_watch_history(self, contenders, min_watched, title, accountid=None):
        logger.info("Writting history record")
        if os.path.isfile(self.history_location):
            write_header = False 
            write_mode = 'a'
        else:
            write_header = True
            write_mode = 'w'

        contenders = 'owc' if contenders else 'owl'
        timestamp = datetime.now().astimezone().isoformat()

        with open(self.history_location, write_mode) as f:
            writer = csv.writer(f)
            if write_header:
               writer.writerow(['Timestamp', 'Account', 'Type', 'Title', 'Minutes'])
            if accountid:
                writer.writerow([timestamp, accountid, contenders, title, min_watched])
            else:
                writer.writerow([timestamp, self.settings['account'], contenders, title, min_watched])
            
    

