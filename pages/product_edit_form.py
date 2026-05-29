import os
import shutil
import time
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QImageReader
from PyQt5 import uic
import config
import db_manager

class ProductEditForm(QWidget):
    """Форма добавления и редактирования товара"""
    form_closed = pyqtSignal()
    
    def __init__(self, main_window, product_id=None):
        super().__init__()
        self.main_window = main_window
        self.product_id = product_id
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "product_form.ui"), self)
        self.current_photo_path = None
        self.original_sku = None  # Сохраняем артикул для проверки удаления
        
        self.ui.lbl_fio.setText(self.main_window.current_fio)
        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self._save)
        self.ui.btn_delete.clicked.connect(self._delete)
        self.ui.btn_load_photo.clicked.connect(self._load_photo)
        
        self._load_combos()
        
        # Разделяем логику создания и редактирования
        if self.product_id is None:
            self.setWindowTitle("Добавление товара")
            self.ui.btn_delete.hide()
            self.ui.lbl_id.hide()
        else:
            self.setWindowTitle(f"Редактирование товара #{self.product_id}")
            self.ui.lbl_id.setText(f"ID: {self.product_id} (только чтение)")
            self._load_data()

    def _load_combos(self):
        """Загружает справочники категорий и производителей в выпадающие списки"""
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            # Категории
            cur.execute('SELECT id_category, category_name FROM categories')
            self.combo_categories = {}
            for row in cur.fetchall():
                d = db_manager.row_to_dict(row)
                name = d.get("category_name")
                val = d.get("id_category")
                if name and val is not None:
                    self.ui.combo_category.addItem(name)
                    self.combo_categories[name] = val

            # Производители
            cur.execute('SELECT id_manufacturer, manufacturer_name FROM manufacturers')
            self.combo_manufacturers = {}
            for row in cur.fetchall():
                d = db_manager.row_to_dict(row)
                name = d.get("manufacturer_name")
                val = d.get("id_manufacturer")
                if name and val is not None:
                    self.ui.combo_manufacturer.addItem(name)
                    self.combo_manufacturers[name] = val
                    
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка БД", f"Не удалось загрузить справочники: {e}")

    def _load_data(self):
        """Подгружает данные существующего товара из БД в поля формы"""
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE id_product=?", (self.product_id,))
            row = db_manager.row_to_dict(cur.fetchone())
            conn.close()
            
            if row:
                self.original_sku = row.get("sku")
                self.ui.line_name.setText(row.get("name", ""))
                self.ui.text_description.setPlainText(row.get("description", ""))
                self.ui.spin_price.setValue(float(row.get("price", 0)))
                self.ui.spin_qty.setValue(int(row.get("quantity", 0)))
                self.ui.spin_discount.setValue(float(row.get("discount", 0)))
                
                # Восстанавливаем выбранные значения в комбобоксах
                cat_name = row.get("category_name")
                if not cat_name and row.get("category_id"):
                    for name, val in self.combo_categories.items():
                        if val == row["category_id"]: cat_name = name
                if cat_name and self.ui.combo_category.findText(cat_name) != -1:
                    self.ui.combo_category.setCurrentText(cat_name)

                man_name = row.get("manufacturer_name")
                if not man_name and row.get("manufacturer_id"):
                    for name, val in self.combo_manufacturers.items():
                        if val == row["manufacturer_id"]: man_name = name
                if man_name and self.ui.combo_manufacturer.findText(man_name) != -1:
                    self.ui.combo_manufacturer.setCurrentText(man_name)
                
                # Загружаем превью фото
                photo_path = row.get("photo_path")
                if photo_path:
                    full_path = os.path.join(config.PHOTOS_DIR, photo_path)
                    if os.path.exists(full_path):
                        self.ui.lbl_photo_preview.setPixmap(QPixmap(full_path).scaled(
                            config.PHOTO_MAX_WIDTH, config.PHOTO_MAX_HEIGHT, aspectRatioMode=1))
                        self.current_photo_path = full_path
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка БД", f"Не удалось загрузить данные товара: {e}")

    def _load_photo(self):
        """Выбор изображения, валидация и масштабирование до 300x200"""
        # Разрешаем популярные графические форматы
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите фото", 
            config.PHOTOS_DIR,  # Открываем сразу в папке photos
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if not file_path:
            return

        # 🔍 Отладка: выводим путь в консоль
        print(f"[DEBUG] Выбран файл: {file_path}")
        print(f"[DEBUG] Файл существует: {os.path.exists(file_path)}")
        print(f"[DEBUG] Размер файла: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} байт")

        # 🔍 Проверяем формат через QImageReader
        reader = QImageReader(file_path)
        reader.setAutoTransform(True)
        
        if not reader.canRead():
            error_msg = reader.errorString()
            print(f"[ERROR] QImageReader не может прочитать файл: {error_msg}")
            
            # Пробуем альтернативный способ проверки
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.warning(
                    self, 
                    "⚠️ Ошибка фото", 
                    f"Файл не распознан как изображение.\n"
                    f"Путь: {file_path}\n"
                    f"Расширение: {os.path.splitext(file_path)[1]}\n"
                    f"Убедитесь, что файл не повреждён и имеет формат PNG, JPG или JPEG."
                )
                return
            else:
                print("[DEBUG] QImage смог прочитать файл, продолжаем...")
                # Если QImage смог прочитать, используем его
                img_scaled = img.scaled(
                    config.PHOTO_MAX_WIDTH, 
                    config.PHOTO_MAX_HEIGHT, 
                    aspectRatioMode=1
                )
        else:
            # QImageReader смог прочитать - используем его
            img = reader.read()
            if img.isNull():
                QMessageBox.warning(
                    self, 
                    "⚠️ Ошибка фото", 
                    "Не удалось загрузить изображение. Файл может быть повреждён."
                )
                return
                
            img_scaled = img.scaled(
                config.PHOTO_MAX_WIDTH, 
                config.PHOTO_MAX_HEIGHT, 
                aspectRatioMode=1
            )
        
        # Показываем превью
        self.ui.lbl_photo_preview.setPixmap(QPixmap.fromImage(img_scaled))
        self.current_photo_path = file_path
        
        QMessageBox.information(
            self, 
            "ℹ️ Обработка", 
            f"Изображение успешно загружено!\n"
            f"Размер: {img_scaled.width()}x{img_scaled.height()} px\n"
            f"Путь: {file_path}"
        )

    def _save(self):
        """Сохраняет новый товар или обновляет существующий"""
        if self.ui.spin_price.value() < 0 or self.ui.spin_qty.value() < 0:
            QMessageBox.warning(self, "⚠️ Ошибка ввода", "Стоимость и количество не могут быть отрицательными. Укажите значения ≥ 0.")
            return
            
        photo_name = os.path.basename(self.current_photo_path) if self.current_photo_path else None
        
        # При замене фото удаляем старое из папки
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
                    if os.path.exists(old_path): os.remove(old_path)
            except: pass

        # Копируем выбранное фото в папку приложения
        if photo_name:
            dst = os.path.join(config.PHOTOS_DIR, photo_name)
            if os.path.abspath(self.current_photo_path) != os.path.abspath(dst):
                try: shutil.copy2(self.current_photo_path, dst)
                except shutil.SameFileError: pass
        
        conn = db_manager.get_connection()
        try:
            cur = conn.cursor()
            cat_name = self.ui.combo_category.currentText()
            cat_id = self.combo_categories.get(cat_name)
            
            man_name = self.ui.combo_manufacturer.currentText()
            man_id = self.combo_manufacturers.get(man_name)
            
            # Поиск поставщика по введённому тексту
            supp_name = self.ui.line_supplier.text().strip()
            cur.execute("SELECT id_supplier FROM suppliers WHERE supplier_name = ?", (supp_name,))
            supp_row = cur.fetchone()
            supp_id = db_manager.row_to_dict(supp_row).get("id_supplier") if supp_row else 1
            
            if self.product_id:
                # Обновление существующей записи (артикул не меняется)
                cur.execute('''UPDATE products SET 
                               name=?, description=?, price=?, unit=?, 
                               category_id=?, manufacturer_id=?, supplier_id=?, 
                               quantity=?, discount=?, photo_path=? 
                               WHERE id_product=?''',
                            (self.ui.line_name.text(), self.ui.text_description.toPlainText(),
                             self.ui.spin_price.value(), self.ui.line_unit.text(), cat_id, man_id,
                             supp_id, self.ui.spin_qty.value(), self.ui.spin_discount.value(), photo_name, self.product_id))
            else:
                # Вставка нового товара (уникальный артикул на основе timestamp)
                sku = f"SKU-{int(time.time())}"
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
        """Удаляет товар, если он не привязан к активным заказам"""
        if not self.product_id or not self.original_sku: return
        
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            # Проверяем вхождение артикула в строку order_articles
            cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE order_articles LIKE ?", (f'%{self.original_sku}%',))
            res = db_manager.row_to_dict(cur.fetchone())
            
            if res.get('cnt', 0) > 0:
                QMessageBox.warning(self, "⚠️ Запрещённая операция", 
                    f"Невозможно удалить товар. Артикул {self.original_sku} присутствует в заказах. Сначала удалите его из заказов.")
                conn.close()
                return
                
            # Удаляем запись из БД
            cur.execute("DELETE FROM products WHERE id_product=?", (self.product_id,))
            conn.commit()
            conn.close()
            
            # Удаляем файл фото, если он существует
            if self.current_photo_path and os.path.exists(self.current_photo_path):
                try: os.remove(self.current_photo_path)
                except: pass
                
            QMessageBox.information(self, "✅ Успех", "Товар удалён.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка БД", f"Ошибка удаления: {e}")
        
    def closeEvent(self, event):
        self.form_closed.emit()
        super().closeEvent(event)
