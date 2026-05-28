import os
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal, QDate
from PyQt5 import uic
import config, db_manager

class OrderEditForm(QWidget):
    form_closed = pyqtSignal()
    
    def __init__(self, main_window, order_id=None):
        super().__init__()
        self.main_window = main_window
        self.order_id = order_id
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "order_form.ui"), self)
        
        # Установка даты заказа на сегодня по умолчанию
        self.ui.date_order.setDate(QDate.currentDate())
        self.ui.lbl_fio.setText(self.main_window.current_fio)
        
        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self._save)
        self.ui.btn_delete.clicked.connect(self._delete)
        
        self._load_combos()
        
        if self.order_id is None:
            self.setWindowTitle("Добавление заказа")
            self.ui.btn_delete.hide()
        else:
            self.setWindowTitle(f"Редактирование заказа #{self.order_id}")
            self._load_order_data()
            
    def _load_combos(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT id_status, status_name FROM statuses')
            self.status_map = {r[1]: r[0] for r in cur.fetchall()}
            for name in self.status_map.keys(): self.ui.combo_status.addItem(name)
            
            cur.execute('SELECT id_pickup_point, pickup_point_address FROM pickup_points')
            self.point_map = {r[1]: r[0] for r in cur.fetchall()}
            for addr in self.point_map.keys(): self.ui.combo_address.addItem(addr)
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка БД", f"Не загрузились справочники заказов: {e}")
            
    def _load_order_data(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM orders WHERE id_order=?', (self.order_id,))
            o = db_manager.row_to_dict(cur.fetchone())
            if o:
                self.ui.line_article.setText(o['order_articles'])
                self.ui.combo_status.setCurrentText(o.get('status_name', ''))
                self.ui.combo_address.setCurrentText(o.get('pickup_point_address', ''))
                self.ui.date_order.setDate(QDate.fromString(o['date_order'], "yyyy-MM-dd"))
                self.ui.date_delivery.setDate(QDate.fromString(o['date_delivery'], "yyyy-MM-dd"))
                self.ui.line_fio_client.setText(o.get('client_fio', ''))
            conn.close()
        except Exception as e: QMessageBox.critical(self, "❌ Ошибка", str(e))

    def _save(self):
        if not self.ui.line_article.text().strip():
            QMessageBox.warning(self, "⚠️ Проверка данных", "Поле 'Артикул заказа' не может быть пустым.")
            return
            
        status_id = self.status_map.get(self.ui.combo_status.currentText())
        point_id = self.point_map.get(self.ui.combo_address.currentText())
        
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            if self.order_id is None:
                cur.execute('''INSERT INTO orders 
                               (order_articles, user_id, status_id, pickup_point_id, code, date_order, date_delivery)
                               VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (self.ui.line_article.text(), self.main_window.current_fio, status_id, 
                             point_id, "AUTO", self.ui.date_order.date().toString("yyyy-MM-dd"), 
                             self.ui.date_delivery.date().toString("yyyy-MM-dd")))
            else:
                cur.execute('''UPDATE orders SET order_articles=?, status_id=?, pickup_point_id=?, 
                               date_order=?, date_delivery=? WHERE id_order=?''',
                            (self.ui.line_article.text(), status_id, point_id,
                             self.ui.date_order.date().toString("yyyy-MM-dd"), 
                             self.ui.date_delivery.date().toString("yyyy-MM-dd"), self.order_id))
            conn.commit(); conn.close()
            QMessageBox.information(self, "✅ Успех", "Заказ сохранён.")
            self.close()
        except Exception as e: QMessageBox.critical(self, "❌ Ошибка БД", str(e))

    def _delete(self):
        try:
            conn = db_manager.get_connection()
            conn.cursor().execute('DELETE FROM orders WHERE id_order=?', (self.order_id,))
            conn.commit(); conn.close()
            QMessageBox.information(self, "✅ Успех", "Заказ удалён.")
            self.close()
        except Exception as e: QMessageBox.critical(self, "❌ Ошибка БД", str(e))
        
    def closeEvent(self, event): self.form_closed.emit(); super().closeEvent(event)
