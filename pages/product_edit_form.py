import os, shutil
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import uic
import config, db_manager

class ProductEditForm(QWidget):
    form_closed = pyqtSignal()
    
    def __init__(self, main_window, product_id=None):
        super().__init__()
        self.main_window = main_window
        self.product_id = product_id
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "product_form.ui"), self)
        self.current_photo_path = None
        
        self.ui.lbl_fio.setText(self.main_window.current_fio)
        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self._save)
        self.ui.btn_delete.clicked.connect(self._delete)
        self.ui.btn_load_photo.clicked.connect(self._load_photo)
        
        self._load_combos()
        
        if self.product_id is None:
            self.setWindowTitle("Добавление товара")
            self.ui.btn_delete.hide()
            self.ui.lbl_id.hide()
        else:
            self.setWindowTitle(f"Редактирование товара #{self.product_id}")
            self.ui.lbl_id.setText(f"ID: {self.product_id} (только чтение)")

    def _load_combos(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT id_category, category_name FROM categories')
            self.combo_categories = {r[1]: r[0] for r in cur.fetchall()}
            for name in self.combo_categories.keys(): self.ui.combo_category.addItem(name)
            
            cur.execute('SELECT id_manufacturer, manufacturer_name FROM manufacturers')
            self.combo_manufacturers = {r[1]: r[0] for r in cur.fetchall()}
            for name in self.combo_manufacturers.keys(): self.ui.combo_manufacturer.addItem(name)
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка", f"Не удалось загрузить справочники: {e}")

    def _load_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фото", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.warning(self, "⚠️ Ошибка фото", "Некорректный файл изображения.")
                return
            self.ui.lbl_photo_preview.setPixmap(QPixmap.fromImage(img.scaled(config.PHOTO_MAX_WIDTH, config.PHOTO_MAX_HEIGHT, aspectRatioMode=1)))
            self.current_photo_path = file_path
            QMessageBox.information(self, "ℹ️ Обработка", f"Изображение приведено к {config.PHOTO_MAX_WIDTH}x{config.PHOTO_MAX_HEIGHT} px.")

    def _save(self):
        if self.ui.spin_price.value() < 0 or self.ui.spin_qty.value() < 0:
            QMessageBox.warning(self, "⚠️ Ошибка ввода", "Стоимость и количество не могут быть отрицательными.")
            return
            
        photo_name = os.path.basename(self.current_photo_path) if self.current_photo_path else None
        if photo_name:
            dst = os.path.join(config.PHOTOS_DIR, photo_name)
            if os.path.abspath(self.current_photo_path) != os.path.abspath(dst):
                try: shutil.copy2(self.current_photo_path, dst)
                except shutil.SameFileError: pass
                
        conn = db_manager.get_connection()
        try:
            cur = conn.cursor()
            cat_id = self.combo_categories.get(self.ui.combo_category.currentText())
            man_id = self.combo_manufacturers.get(self.ui.combo_manufacturer.currentText())
            
            cur.execute('''INSERT INTO products 
                           (sku, name, description, price, unit, category_id, manufacturer_id, 
                            supplier_id, quantity, discount, photo_path)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        ("NEW-SKU", self.ui.line_name.text(), self.ui.text_description.toPlainText(),
                         self.ui.spin_price.value(), self.ui.line_unit.text(), cat_id, man_id,
                         1, self.ui.spin_qty.value(), self.ui.spin_discount.value(), photo_name))
            conn.commit()
            QMessageBox.information(self, "✅ Успех", "Товар успешно добавлен.")
            self.close()
        except Exception as e: 
            conn.rollback()
            QMessageBox.critical(self, "❌ Ошибка БД", f"Не удалось сохранить: {e}")

    def _delete(self): QMessageBox.information(self, "ℹ️ Удаление", "Проверка наличия в заказах будет на следующем шаге.")
    def closeEvent(self, event): self.form_closed.emit(); super().closeEvent(event)
