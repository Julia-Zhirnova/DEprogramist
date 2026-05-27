import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtGui import QIcon
import config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ООО «Обувь» — Учёт товаров и заказов")
        self.setWindowIcon(QIcon(config.ICON_PATH))
        self.resize(1100, 750)

        self.current_role = config.ROLE_GUEST
        self.current_fio = "Гость"

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Загружаем страницу входа
        from pages.login_page import LoginPage
        self.login_page = LoginPage(self)
        self.stack.addWidget(self.login_page)

        self._load_stylesheet()

    def _load_stylesheet(self):
        path = os.path.join(config.BASE_DIR, "styles.qss")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def switch_to(self, widget):
        idx = self.stack.addWidget(widget)
        self.stack.setCurrentIndex(idx)

    def reset_session(self):
        self.current_role = config.ROLE_GUEST
        self.current_fio = "Гость"
        self.stack.setCurrentWidget(self.login_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(config.ICON_PATH))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
