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
        self.ui.line_fio_client.hide(); self.ui.lbl_fio_client.hide()
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
            self._load_data()

    def _load_combos(self):
        try:
            conn = db_manager.get_connection()
            self.status_map, self.point_map = {}, {}
            for r in conn.cursor().execute("SELECT id_status, status_name FROM statuses").fetchall():
                d = db_manager.row_to_dict(r); self.status_map[d.get("status_name")]=d.get("id_status"); self.ui.combo_status.addItem(d.get("status_name"))
            for r in conn.cursor().execute("SELECT id_pickup_point, pickup_point_address FROM pickup_points").fetchall():
                d = db_manager.row_to_dict(r); self.point_map[d.get("pickup_point_address")]=d.get("id_pickup_point"); self.ui.combo_address.addItem(d.get("pickup_point_address"))
            conn.close()
        except Exception as e: QMessageBox.critical(self, "❌ Ошибка БД", str(e))

    def _load_data(self):
        try:
            conn = db_manager.get_connection()
            row = db_manager.row_to_dict(conn.cursor().execute("SELECT o.*, s.status_name, pp.pickup_point_address FROM orders o LEFT JOIN statuses s ON o.status_id=s.id_status LEFT JOIN pickup_points pp ON o.pickup_point_id=pp.id_pickup_point WHERE o.id_order=?", (self.order_id,)).fetchone())
            conn.close()
            if row:
                self.ui.line_article.setText(row.get("order_articles",""))
                if row.get("status_name") and self.ui.combo_status.findText(row["status_name"])!=-1: self.ui.combo_status.setCurrentText(row["status_name"])
                if row.get("pickup_point_address") and self.ui.combo_address.findText(row["pickup_point_address"])!=-1: self.ui.combo_address.setCurrentText(row["pickup_point_address"])
                if row.get("date_order"): self.ui.date_order.setDate(QDate.fromString(row["date_order"], "yyyy-MM-dd"))
                if row.get("date_delivery"): self.ui.date_delivery.setDate(QDate.fromString(row["date_delivery"], "yyyy-MM-dd"))
        except Exception as e: QMessageBox.critical(self, "❌ Ошибка БД", str(e))

    def _save(self):
        if not self.ui.line_article.text().strip(): QMessageBox.warning(self, "⚠️ Проверка", "Артикул заказа не может быть пустым."); return
        sid = self.status_map.get(self.ui.combo_status.currentText())
        pid = self.point_map.get(self.ui.combo_address.currentText())
        conn = db_manager.get_connection()
        uid = db_manager.row_to_dict(conn.cursor().execute("SELECT id_user FROM users WHERE fio=?", (self.main_window.current_fio,)).fetchone()).get("id_user") or 1
        try:
            cur = conn.cursor()
            if self.order_id is None:
                cur.execute("INSERT INTO orders (order_articles, user_id, status_id, pickup_point_id, code, date_order, date_delivery) VALUES (?,?,?,?,?,?,?)",
                            (self.ui.line_article.text(), uid, sid, pid, "AUTO", self.ui.date_order.date().toString("yyyy-MM-dd"), self.ui.date_delivery.date().toString("yyyy-MM-dd")))
            else:
                cur.execute("UPDATE orders SET order_articles=?, status_id=?, pickup_point_id=?, date_order=?, date_delivery=? WHERE id_order=?",
                            (self.ui.line_article.text(), sid, pid, self.ui.date_order.date().toString("yyyy-MM-dd"), self.ui.date_delivery.date().toString("yyyy-MM-dd"), self.order_id))
            conn.commit(); conn.close()
            QMessageBox.information(self, "✅ Успех", "Заказ сохранён."); self.close()
        except Exception as e: conn.rollback(); conn.close(); QMessageBox.critical(self, "❌ Ошибка БД", str(e))

    def _delete(self):
        if not self.order_id: return
        if QMessageBox.question(self, "⚠️ Подтверждение", "Удалить заказ?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.No: return
        try:
            conn = db_manager.get_connection()
            conn.cursor().execute("DELETE FROM orders WHERE id_order=?", (self.order_id,))
            conn.commit(); conn.close()
            QMessageBox.information(self, "✅ Успех", "Удалено."); self.close()
        except Exception as e: QMessageBox.critical(self, "❌ Ошибка БД", str(e))
    def closeEvent(self, event): self.form_closed.emit(); super().closeEvent(event)
