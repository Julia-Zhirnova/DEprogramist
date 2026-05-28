import os
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
import config
import db_manager

class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "login.ui"), self)
        
        # Подключаем кнопки
        self.ui.btn_login.clicked.connect(self.on_login)
        self.ui.btn_guest.clicked.connect(self.on_guest)
        
        # Стилизуем метки ошибок
        for lbl in [self.ui.lbl_login_err, self.ui.lbl_pass_err]:
            lbl.setStyleSheet("color: #FF0000; font-weight: bold; font-style: italic;")
            lbl.hide()
        
    def on_login(self):
        login = self.ui.login_input.text().strip()
        password = self.ui.password_input.text().strip()
        
        # Сброс ошибок
        self.ui.lbl_login_err.hide()
        self.ui.lbl_pass_err.hide()
        
        # Валидация: показываем ОБЕ ошибки одновременно, если оба поля пустые
        errors = []
        if not login:
            self.ui.lbl_login_err.setText("Логин не может быть пустым")
            self.ui.lbl_login_err.show()
            errors.append("login")
        if not password:
            self.ui.lbl_pass_err.setText("Пароль не может быть пустым")
            self.ui.lbl_pass_err.show()
            errors.append("password")
            
        if errors:
            return  # Прерываем, если есть ошибки
            
        # Проверка в БД
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT id_user, role_id, fio FROM users WHERE login=? AND password=?",
                (login, password)
            )
            user = cur.fetchone()
            conn.close()
            
            if user:
                self.main_window.current_role = user["role_id"]
                self.main_window.current_fio = user["fio"]
                self._proceed_to_products()
            else:
                QMessageBox.critical(
                    self,
                    "❌ Ошибка авторизации",
                    "Пользователь не найден в базе данных. Проверьте правильность логина и пароля. При повторной ошибке обратитесь к администратору системы."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Системная ошибка",
                f"Не удалось подключиться к базе данных: {str(e)}"
            )
    
    def on_guest(self):
        self.main_window.current_role = config.ROLE_GUEST
        self.main_window.current_fio = "Гость"
        self._proceed_to_products()
    
    def _proceed_to_products(self):
        from pages.products_page import ProductsPage
        products_page = ProductsPage(self.main_window)
        self.main_window.switch_to(products_page)
