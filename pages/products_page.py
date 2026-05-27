from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import os
import config

class ProductsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "products.ui"), self)
        
        # Отображаем ФИО (если не гость)
        if self.main_window.current_role != config.ROLE_GUEST:
            self.ui.lbl_fio.setText(self.main_window.current_fio)
        else:
            self.ui.lbl_fio.hide()
        
        # Скрываем кнопки управления для гостя/клиента
        if self.main_window.current_role in [config.ROLE_GUEST, config.ROLE_CLIENT]:
            self.ui.line_search.hide()
            self.ui.combo_sort.hide()
            self.ui.combo_filter.hide()
            self.ui.btn_orders.hide()
            self.ui.btn_add_product.hide()
        
        # Кнопка выхода
        self.ui.btn_logout.clicked.connect(self.on_logout)
        
    def on_logout(self):
        self.main_window.reset_session()
