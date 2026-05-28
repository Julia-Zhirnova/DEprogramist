import os
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMessageBox
from PyQt5 import uic
import config
import db_manager

class OrdersPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "orders.ui"), self)
        
        self.ui.lbl_fio.setText(self.main_window.current_fio)
        self.ui.btn_back.clicked.connect(self._go_back)
        self._load_orders()
        
        if self.main_window.current_role != config.ROLE_ADMIN:
            self.ui.btn_add_order.hide()
        else:
            self.ui.btn_add_order.clicked.connect(self._add_order)
            
    def _load_orders(self):
        self.ui.list_orders.clear()
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute("""SELECT o.*, s.status_name, p.address, u.fio as client_fio
                           FROM orders o
                           LEFT JOIN statuses s ON o.status_id = s.id_status
                           LEFT JOIN pickup_points p ON o.point_id = p.id_point
                           LEFT JOIN users u ON o.user_id = u.id_user
                           ORDER BY o.date_order DESC""")
            for row in cur.fetchall():
                item = QListWidgetItem()
                card = (f"<b>Заказ №{row['id_order']}</b> | {row['order_articles']}<br/>"
                        f"<small>Клиент: {row['client_fio']}</small><br/>"
                        f"<small>Статус: {row['status_name']}</small> | "
                        f"<small>Пункт: {row['address']}</small><br/>"
                        f"<small>Заказан: {row['date_order']}</small> | "
                        f"<small>Выдача: {row['date_delivery']}</small>")
                item.setText(card)
                self.ui.list_orders.addItem(item)
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка", f"Не удалось загрузить заказы: {e}")
            
    def _add_order(self):
        QMessageBox.information(self, "ℹ️ В разработке", "Форма добавления заказа будет реализована на следующем шаге.")
        
    def _go_back(self):
        from pages.products_page import ProductsPage
        self.main_window.switch_to(ProductsPage(self.main_window))
