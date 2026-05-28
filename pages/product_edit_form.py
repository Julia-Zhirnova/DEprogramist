import os
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic
import config
import db_manager

class ProductEditForm(QWidget):
    form_closed = pyqtSignal()
    
    def __init__(self, main_window, product_id=None):
        super().__init__()
        self.main_window = main_window
        self.product_id = product_id
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "product_form.ui"), self)
        
        self.ui.lbl_fio.setText(self.main_window.current_fio)
        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self._save)
        self.ui.btn_delete.clicked.connect(self._delete)
        
        if self.product_id is None:
            self.setWindowTitle("Добавление товара")
            self.ui.btn_delete.hide()
            self.ui.lbl_id.hide()
        else:
            self.setWindowTitle(f"Редактирование товара #{self.product_id}")
            self.ui.lbl_id.setText(f"ID: {self.product_id} (только чтение)")
            self._load_data()
            
    def _load_data(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE id_product=?", (self.product_id,))
            row = cur.fetchone()
            if row:
                self.ui.line_name.setText(row['name'])
                self.ui.text_description.setPlainText(row['description'])
                self.ui.spin_price.setValue(row['price'])
                self.ui.spin_qty.setValue(row['qty'])
                self.ui.spin_discount.setValue(row['discount'])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка", f"Не удалось загрузить данные: {e}")
            
    def _save(self):
        QMessageBox.information(self, "ℹ️ Сохранение", "Данные сохранены (заглушка). Список товаров обновится.")
        self.close()
        
    def _delete(self):
        QMessageBox.information(self, "ℹ️ Удаление", "Товар удалён (заглушка). Список товаров обновится.")
        self.close()
        
    def closeEvent(self, event):
        self.form_closed.emit()
        super().closeEvent(event)
