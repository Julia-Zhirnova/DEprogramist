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
        self.orders_data = []

        self.ui.lbl_fio.setText(self.main_window.current_fio)
        self.ui.btn_back.clicked.connect(self._go_back)

        if self.main_window.current_role != config.ROLE_ADMIN:
            self.ui.btn_add_order.hide()
        else:
            self.ui.btn_add_order.clicked.connect(self._add_order)

        self._load_orders()

    def _load_orders(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            # Используем чистые имена колонок (после fix_db.py)
            cur.execute('''SELECT o.id_order, o.order_articles, o.date_order, o.date_delivery,
                                  s.status_name, pp.pickup_point_address as address, u.fio as client_fio
                            FROM orders o
                            LEFT JOIN statuses s ON o.status_id = s.id_status
                            LEFT JOIN pickup_points pp ON o.pickup_point_id = pp.id_pickup_point
                            LEFT JOIN users u ON o.user_id = u.id_user
                            ORDER BY o.date_order DESC''')
            self.orders_data = [db_manager.row_to_dict(r) for r in cur.fetchall()]
            conn.close()
        except Exception as e:
            print(f"❌ Ошибка загрузки заказов: {e}")
            QMessageBox.critical(self, "❌ Ошибка БД", f"Не удалось загрузить заказы: {e}")
            self.orders_data = []
        self._render_orders()

    def _render_orders(self):
        self.ui.list_orders.clear()
        for o in self.orders_data:
            item = QListWidgetItem()
            html = (f"<b>Заказ №{o.get('id_order', '-')}</b> | {o.get('order_articles', '-')}"
                    f"<br/><small>Клиент: {o.get('client_fio', '-')}</small><br/>"
                    f"<small>Статус: {o.get('status_name', '-')}</small> | "
                    f"<small>Пункт: {o.get('address', '-')}</small><br/>"
                    f"<small>Заказан: {o.get('date_order', '-')}</small> | "
                    f"<small>Выдача: {o.get('date_delivery', '-')}</small>")
            item.setText(html)
            # PyQt5 автоматически рендерит HTML-теги. Принудительная установка роли вызывает краш.
            self.ui.list_orders.addItem(item)

    def _add_order(self):
        QMessageBox.information(self, "ℹ️ В разработке", "Форма добавления заказа будет реализована на следующем шаге.")

    def _go_back(self):
        for i in range(self.main_window.stack.count()):
            w = self.main_window.stack.widget(i)
            if w.__class__.__name__ == 'ProductsPage':
                self.main_window.stack.setCurrentWidget(w)
                return
