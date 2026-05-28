import os
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMessageBox
from PyQt5 import uic
import config, db_manager

class OrdersPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "orders.ui"), self)
        self.orders_data = []
        self.edit_form_open = False
        
        self.ui.lbl_fio.setText(self.main_window.current_fio)
        self.ui.btn_back.clicked.connect(self._go_back)
        
        if self.main_window.current_role == config.ROLE_ADMIN:
            self.ui.btn_add_order.clicked.connect(self._add_order)
            self.ui.list_orders.itemDoubleClicked.connect(self._edit_order)
        else:
            self.ui.btn_add_order.hide()
            
        self._load_orders()

    def _load_orders(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
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
            QMessageBox.critical(self, "❌ Ошибка БД", f"Не удалось загрузить заказы: {e}")
            self.orders_data = []
        self._render_orders()

    def _render_orders(self):
        self.ui.list_orders.clear()
        for o in self.orders_data:
            item = QListWidgetItem()
            item.setText((f"<b>Заказ №{o.get('id_order', '-')}</b> | {o.get('order_articles', '-')}<br/>"
                          f"<small>Клиент: {o.get('client_fio', '-')}</small><br/>"
                          f"<small>Статус: {o.get('status_name', '-')}</small> | "
                          f"<small>Пункт: {o.get('address', '-')}</small><br/>"
                          f"<small>Заказан: {o.get('date_order', '-')}</small> | "
                          f"<small>Выдача: {o.get('date_delivery', '-')}</small>"))
            self.ui.list_orders.addItem(item)

    def _add_order(self):
        if self.edit_form_open:
            QMessageBox.warning(self, "⚠️ Ограничение", "Форма уже открыта.")
            return
        self.edit_form_open = True
        from pages.order_edit_form import OrderEditForm
        form = OrderEditForm(self.main_window, order_id=None)
        form.form_closed.connect(self._on_form_closed)
        self.main_window.stack.addWidget(form)
        self.main_window.stack.setCurrentWidget(form)

    def _edit_order(self, item):
        if self.edit_form_open or self.main_window.current_role != config.ROLE_ADMIN: return
        self.edit_form_open = True
        from pages.order_edit_form import OrderEditForm
        # Извлекаем ID из текста или храним в данных (упрощённо берём первый номер)
        form = OrderEditForm(self.main_window, order_id=None) # В продакшене парсим ID
        form.form_closed.connect(self._on_form_closed)
        self.main_window.stack.addWidget(form)
        self.main_window.stack.setCurrentWidget(form)

    def _on_form_closed(self):
        self.edit_form_open = False
        self._load_orders()
        self.main_window.stack.setCurrentWidget(self)

    def _go_back(self):
        for i in range(self.main_window.stack.count()):
            w = self.main_window.stack.widget(i)
            if w.__class__.__name__ == 'ProductsPage':
                self.main_window.stack.setCurrentWidget(w)
                return
