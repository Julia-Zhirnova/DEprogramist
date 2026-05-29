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
        
        # Скрываем ФИО клиента (по ТЗ не требуется на форме ввода)
        self.ui.line_fio_client.hide()
        self.ui.lbl_fio_client.hide()
        
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
            self._load_data() # Подгрузка данных заказа
            
    def _load_combos(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            cur.execute('SELECT id_status, status_name FROM statuses')
            self.status_map = {}
            for row in cur.fetchall():
                d = db_manager.row_to_dict(row)
                self.status_map[d.get("status_name")] = d.get("id_status")
                self.ui.combo_status.addItem(d.get("status_name"))
                
            cur.execute('SELECT id_pickup_point, pickup_point_address FROM pickup_points')
            self.point_map = {}
            for row in cur.fetchall():
                d = db_manager.row_to_dict(row)
                self.point_map[d.get("pickup_point_address")] = d.get("id_pickup_point")
                self.ui.combo_address.addItem(d.get("pickup_point_address"))
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка БД", f"Не загрузились справочники: {e}")
            
    def _load_data(self):
        """Подгрузка данных заказа"""
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            # JOIN для получения имен статусов и адресов
            cur.execute('''SELECT o.*, s.status_name, pp.pickup_point_address 
                           FROM orders o
                           LEFT JOIN statuses s ON o.status_id = s.id_status
                           LEFT JOIN pickup_points pp ON o.pickup_point_id = pp.id_pickup_point
                           WHERE o.id_order=?''', (self.order_id,))
            row = db_manager.row_to_dict(cur.fetchone())
            conn.close()
            
            if row:
                self.ui.line_article.setText(row.get("order_articles", ""))
                self.ui.line_fio_client.setText(row.get("client_fio", "")) # Если нужно показать
                
                status_name = row.get("status_name")
                if status_name and self.ui.combo_status.findText(status_name) != -1:
                    self.ui.combo_status.setCurrentText(status_name)
                    
                address = row.get("pickup_point_address")
                if address and self.ui.combo_address.findText(address) != -1:
                    self.ui.combo_address.setCurrentText(address)
                    
                # Даты
                d_order = row.get("date_order")
                if d_order: self.ui.date_order.setDate(QDate.fromString(d_order, "yyyy-MM-dd"))
                d_del = row.get("date_delivery")
                if d_del: self.ui.date_delivery.setDate(QDate.fromString(d_del, "yyyy-MM-dd"))
                
        except Exception as e: 
            QMessageBox.critical(self, "❌ Ошибка", str(e))

    def _save(self):
        if not self.ui.line_article.text().strip():
            QMessageBox.warning(self, "⚠️ Проверка данных", "Поле 'Артикул заказа' не может быть пустым.")
            return
            
        status_name = self.ui.combo_status.currentText()
        status_id = self.status_map.get(status_name)
        
        address = self.ui.combo_address.currentText()
        point_id = self.point_map.get(address)
        
        # Определяем ID пользователя (для привязки заказа)
        conn = db_manager.get_connection()
        cur = conn.cursor()
        try:
            cur.execute('SELECT id_user FROM users WHERE fio=?', (self.main_window.current_fio,))
            res = db_manager.row_to_dict(cur.fetchone())
            user_id = res.get("id_user") if res else 1
        except: user_id = 1
        
        try:
            if self.order_id is None:
                cur.execute('''INSERT INTO orders 
                               (order_articles, user_id, status_id, pickup_point_id, code, date_order, date_delivery)
                               VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (self.ui.line_article.text(), user_id, status_id, point_id, 
                             "AUTO", self.ui.date_order.date().toString("yyyy-MM-dd"), 
                             self.ui.date_delivery.date().toString("yyyy-MM-dd")))
            else:
                cur.execute('''UPDATE orders SET order_articles=?, status_id=?, pickup_point_id=?, 
                               date_order=?, date_delivery=? WHERE id_order=?''',
                            (self.ui.line_article.text(), status_id, point_id,
                             self.ui.date_order.date().toString("yyyy-MM-dd"), 
                             self.ui.date_delivery.date().toString("yyyy-MM-dd"), self.order_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "✅ Успех", "Заказ сохранён.")
            self.close()
        except Exception as e: 
            conn.rollback()
            conn.close()
            QMessageBox.critical(self, "❌ Ошибка БД", str(e))

    def _delete(self):
        """Удаление заказа"""
        if not self.order_id: return
        try:
            conn = db_manager.get_connection()
            conn.cursor().execute('DELETE FROM orders WHERE id_order=?', (self.order_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "✅ Успех", "Заказ удалён.")
            self.close()
        except Exception as e: 
            QMessageBox.critical(self, "❌ Ошибка БД", str(e))
        
    def closeEvent(self, event): self.form_closed.emit(); super().closeEvent(event)
