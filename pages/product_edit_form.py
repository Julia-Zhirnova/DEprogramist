import os, shutil, time
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QImageReader
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
        self.original_sku = None
        
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
            self._load_data()

    def _load_combos(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            self.combo_categories, self.combo_manufacturers = {}, {}
            for sql, target, combo in [('SELECT id_category, category_name FROM categories', self.combo_categories, self.ui.combo_category),
                                       ('SELECT id_manufacturer, manufacturer_name FROM manufacturers', self.combo_manufacturers, self.ui.combo_manufacturer)]:
                for r in cur.execute(sql).fetchall():
                    d = db_manager.row_to_dict(r)
                    name, val = d.get(list(d.keys())[1]), d.get(list(d.keys())[0])
                    if name and val is not None:
                        combo.addItem(name)
                        target[name] = val
            conn.close()
        except Exception as e: QMessageBox.critical(self, "❌ Ошибка БД", str(e))

    def _load_data(self):
        try:
            conn = db_manager.get_connection()
            row = db_manager.row_to_dict(conn.cursor().execute("SELECT * FROM products WHERE id_product=?", (self.product_id,)).fetchone())
            conn.close()
            if row:
                self.original_sku = row.get("sku")
                self.ui.line_name.setText(row.get("name", ""))
                self.ui.text_description.setPlainText(row.get("description", ""))
                self.ui.spin_price.setValue(float(row.get("price", 0)))
                self.ui.spin_qty.setValue(int(row.get("quantity", 0)))
                self.ui.spin_discount.setValue(int(float(row.get("discount", 0))))
                for combo, target, key in [(self.ui.combo_category, self.combo_categories, "category_id"),
                                           (self.ui.combo_manufacturer, self.combo_manufacturers, "manufacturer_id")]:
                    name = row.get(f"{key.split('_')[0]}_name") or next((n for n,v in target.items() if v == row.get(key)), None)
                    if name and combo.findText(name) != -1: combo.setCurrentText(name)
                photo = row.get("photo_path")
                if photo and os.path.exists(os.path.join(config.PHOTOS_DIR, photo)):
                    self.ui.lbl_photo_preview.setPixmap(QPixmap(os.path.join(config.PHOTOS_DIR, photo)).scaled(config.PHOTO_MAX_WIDTH, config.PHOTO_MAX_HEIGHT, 1))
                    self.current_photo_path = os.path.join(config.PHOTOS_DIR, photo)
        except Exception as e: QMessageBox.critical(self, "❌ Ошибка БД", str(e))

    def _load_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите PNG-фото", config.PHOTOS_DIR, "Изображения (*.png)")
        if not path: return
        img = QImage(path)
        if img.isNull(): QMessageBox.warning(self, "⚠️ Ошибка фото", "Файл не распознан. Используйте PNG."); return
        self.ui.lbl_photo_preview.setPixmap(QPixmap.fromImage(img.scaled(config.PHOTO_MAX_WIDTH, config.PHOTO_MAX_HEIGHT, 1)))
        self.current_photo_path = path

    def _save(self):
        if self.ui.spin_price.value() < 0 or self.ui.spin_qty.value() < 0:
            QMessageBox.warning(self, "⚠️ Ошибка ввода", "Цена и количество ≥ 0."); return
        photo = os.path.basename(self.current_photo_path) if self.current_photo_path else None
        if self.product_id and photo:
            try:
                conn = db_manager.get_connection()
                old = db_manager.row_to_dict(conn.cursor().execute("SELECT photo_path FROM products WHERE id_product=?", (self.product_id,)).fetchone()).get("photo_path")
                conn.close()
                if old and old != photo:
                    p = os.path.join(config.PHOTOS_DIR, old)
                    if os.path.exists(p): os.remove(p)
            except: pass
        if photo:
            dst = os.path.join(config.PHOTOS_DIR, photo)
            if os.path.abspath(self.current_photo_path) != os.path.abspath(dst):
                try: shutil.copy2(self.current_photo_path, dst)
                except: pass
        conn = db_manager.get_connection()
        try:
            cur = conn.cursor()
            cid = self.combo_categories.get(self.ui.combo_category.currentText())
            mid = self.combo_manufacturers.get(self.ui.combo_manufacturer.currentText())
            sid = db_manager.row_to_dict(cur.execute("SELECT id_supplier FROM suppliers WHERE supplier_name=?", (self.ui.line_supplier.text(),)).fetchone()).get("id_supplier") or 1
            if self.product_id:
                cur.execute("UPDATE products SET name=?, description=?, price=?, unit=?, category_id=?, manufacturer_id=?, supplier_id=?, quantity=?, discount=?, photo_path=? WHERE id_product=?",
                            (self.ui.line_name.text(), self.ui.text_description.toPlainText(), self.ui.spin_price.value(), self.ui.line_unit.text(), cid, mid, sid, self.ui.spin_qty.value(), self.ui.spin_discount.value(), photo, self.product_id))
            else:
                cur.execute("INSERT INTO products (sku, name, description, price, unit, category_id, manufacturer_id, supplier_id, quantity, discount, photo_path) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                            (f"SKU-{int(time.time())}", self.ui.line_name.text(), self.ui.text_description.toPlainText(), self.ui.spin_price.value(), self.ui.line_unit.text(), cid, mid, sid, self.ui.spin_qty.value(), self.ui.spin_discount.value(), photo))
            conn.commit(); conn.close()
            QMessageBox.information(self, "✅ Успех", "Сохранено.")
            self.close()
        except Exception as e: conn.rollback(); conn.close(); QMessageBox.critical(self, "❌ Ошибка БД", str(e))

    def _delete(self):
        if not self.product_id or not self.original_sku: return
        if QMessageBox.question(self, "⚠️ Подтверждение", f"Удалить товар {self.original_sku}?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.No: return
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            if db_manager.row_to_dict(cur.execute("SELECT COUNT(*) as c FROM orders WHERE order_articles LIKE ?", (f'%{self.original_sku}%',)).fetchone()).get('c', 0) > 0:
                QMessageBox.warning(self, "⚠️ Запрещено", "Товар в заказах. Сначала удалите из заказов."); conn.close(); return
            cur.execute("DELETE FROM products WHERE id_product=?", (self.product_id,))
            conn.commit(); conn.close()
            if self.current_photo_path and os.path.exists(self.current_photo_path): os.remove(self.current_photo_path)
            QMessageBox.information(self, "✅ Успех", "Удалено."); self.close()
        except Exception as e: QMessageBox.critical(self, "❌ Ошибка БД", str(e))
    def closeEvent(self, event): self.form_closed.emit(); super().closeEvent(event)
