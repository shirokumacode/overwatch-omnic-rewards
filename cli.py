from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import logging

from settings import SettingsManager
from stats import Stats
from checkviewer import CheckViewer

logger = logging.getLogger(__name__)

class CLIApp(QObject):
    def __init__(self, settings: SettingsManager, stats: Stats, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.stats = stats

        if not self.settings.get("account"):
            logger.error("No account set. Please setup and account on config.json or through the GUI")
            QCoreApplication.instance().exit()

        self.check_viewer = CheckViewer(
            self.settings.get('account'),
            owl_flag=self.settings.get('owl'),
            owc_flag=self.settings.get('owc'),
            min_check=self.settings.get('min_check')
        )

        self.check_viewer.check_progress.connect(self.update_check_progress)
        self.check_viewer.watching_owl.connect(self.update_watching_owl)
        self.check_viewer.watching_owc.connect(self.update_watching_owc)
        self.check_viewer.error.connect(self.update_error)

        self.check_viewer.run()

    @pyqtSlot(int)
    def update_check_progress(self, min_remaining=None):
        if min_remaining:
            logger.info(f"Not Live - {min_remaining}min until next check")

    @pyqtSlot(int, str, bool)
    def update_watching_owl(self, min_watching, title, end):
        self.stats.set_record(False, min_watching, title, self.settings.get('account'))
        if not end:
            logger.info(f"Watching OWL for {min_watching}min")
        else:
            self.stats.write_record()
            logger.info(f"Watched {min_watching}mins of OWL - {title}")

    @pyqtSlot(int, str, bool)
    def update_watching_owc(self, min_watching, title, end):
        self.stats.set_record(True, min_watching, title, self.settings.get('account'))
        if not end:
            logger.info(f"Watching OWC for {min_watching}min")
        else:
            self.stats.write_record()
            logger.info(f"Watched {min_watching}mins of OWC - {title}")

    @pyqtSlot(str, bool)
    def update_error(self, error_msg, notification):
        self.stats.write_record()
        if notification:
            QTimer.singleShot(60000, self.unfreeze_checkviewer)

    def unfreeze_checkviewer(self):
        if not self.check_viewer.check_timer.isActive() and not self.check_viewer.watcher_timer.isActive():
            self.check_viewer.start_check_timer()

    @pyqtSlot() 
    def prepare_to_exit(self):
        logger.info("Preparing to exit")
        self.stats.write_record()
        self.check_viewer.prepare_to_exit(exit_signal=False)








