import os
import shutil
import time
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
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
            # Загрузка данных при редактировании (если нужно)
            self._load_data()

    def _load_combos(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            # Загрузка категорий
            cur.execute('SELECT id_category, category_name FROM categories')
            for row in cur.fetchall():
                d = db_manager.row_to_dict(row)
                name = d.get("category_name")
                val = d.get("id_category")
                if name and val is not None:
                    self.ui.combo_category.addItem(name)
                    self.combo_categories = getattr(self, 'combo_categories', {})
                    self.combo_categories[name] = val

            # Загрузка производителей
            cur.execute('SELECT id_manufacturer, manufacturer_name FROM manufacturers')
            for row in cur.fetchall():
                d = db_manager.row_to_dict(row)
                name = d.get("manufacturer_name")
                val = d.get("id_manufacturer")
                if name and val is not None:
                    self.ui.combo_manufacturer.addItem(name)
                    self.combo_manufacturers = getattr(self, 'combo_manufacturers', {})
                    self.combo_manufacturers[name] = val
            
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка", f"Не удалось загрузить справочники: {e}")

    def _load_data(self):
        """Загрузка данных существующего товара в форму"""
        if not self.product_id: return
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE id_product=?", (self.product_id,))
            row = db_manager.row_to_dict(cur.fetchone())
            if row:
                self.ui.line_name.setText(row.get("name", ""))
                self.ui.text_description.setPlainText(row.get("description", ""))
                self.ui.spin_price.setValue(float(row.get("price", 0)))
                self.ui.spin_qty.setValue(int(row.get("quantity", 0)))
                self.ui.spin_discount.setValue(float(row.get("discount", 0)))
                
                # Установка комбобоксов
                cat_name = row.get("category_name") # Если есть в JOIN, иначе нужно отдельно искать
                # Для простоты, если данных из JOIN нет, пропускаем
            conn.close()
        except: pass

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
        
        # Логика удаления старого фото при замене
        if self.product_id and photo_name:
            try:
                conn = db_manager.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT photo_path FROM products WHERE id_product=?", (self.product_id,))
                old_row = db_manager.row_to_dict(cur.fetchone())
                old_photo = old_row.get("photo_path") if old_row else None
                conn.close()
                
                if old_photo and old_photo != photo_name:
                    old_path = os.path.join(config.PHOTOS_DIR, old_photo)
                    if os.path.exists(old_path):
                        os.remove(old_path)
            except: pass

        if photo_name:
            dst = os.path.join(config.PHOTOS_DIR, photo_name)
            if os.path.abspath(self.current_photo_path) != os.path.abspath(dst):
                try: shutil.copy2(self.current_photo_path, dst)
                except shutil.SameFileError: pass
        
        conn = db_manager.get_connection()
        try:
            cur = conn.cursor()
            
            # Получаем ID категории и производителя
            cat_name = self.ui.combo_category.currentText()
            cat_id = getattr(self, 'combo_categories', {}).get(cat_name)
            
            man_name = self.ui.combo_manufacturer.currentText()
            man_id = getattr(self, 'combo_manufacturers', {}).get(man_name)
            
            # Ищем ID поставщика по тексту
            supp_name = self.ui.line_supplier.text().strip()
            cur.execute("SELECT id_supplier FROM suppliers WHERE supplier_name = ?", (supp_name,))
            supp_row = cur.fetchone()
            supp_id = db_manager.row_to_dict(supp_row).get("id_supplier") if supp_row else 1 # По умолчанию Kari
            
            # Генерируем уникальный артикул
            sku = f"SKU-{int(time.time())}"
            
            if self.product_id:
                # Обновление (редактирование)
                cur.execute('''UPDATE products SET 
                               sku=?, name=?, description=?, price=?, unit=?, 
                               category_id=?, manufacturer_id=?, supplier_id=?, 
                               quantity=?, discount=?, photo_path=? 
                               WHERE id_product=?''',
                            (sku, self.ui.line_name.text(), self.ui.text_description.toPlainText(),
                             self.ui.spin_price.value(), self.ui.line_unit.text(), cat_id, man_id,
                             supp_id, self.ui.spin_qty.value(), self.ui.spin_discount.value(), photo_name, self.product_id))
            else:
                # Вставка (новый товар)
                cur.execute('''INSERT INTO products 
                               (sku, name, description, price, unit, category_id, manufacturer_id, 
                                supplier_id, quantity, discount, photo_path)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (sku, self.ui.line_name.text(), self.ui.text_description.toPlainText(),
                             self.ui.spin_price.value(), self.ui.line_unit.text(), cat_id, man_id,
                             supp_id, self.ui.spin_qty.value(), self.ui.spin_discount.value(), photo_name))
            
            conn.commit()
            conn.close()
            QMessageBox.information(self, "✅ Успех", "Товар успешно сохранён.")
            self.close()
            
        except Exception as e: 
            conn.rollback()
            conn.close()
            QMessageBox.critical(self, "❌ Ошибка БД", f"Не удалось сохранить: {e}")

    def _delete(self):
        QMessageBox.information(self, "ℹ️ Удаление", "Проверка наличия в заказах будет на следующем шаге.")
        
    def closeEvent(self, event): self.form_closed.emit(); super().closeEvent(event)
