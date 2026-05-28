import os
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5 import uic
import config
import db_manager

class ProductsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "products.ui"), self)
        
        self._setup_header()
        self._setup_role_visibility()
        self._load_products()
        self._connect_signals()
        self.edit_form_open = False
        
    def _setup_header(self):
        title_label = QLabel("Каталог товаров")
        title_label.setFont(QFont(config.FONT_FAMILY, 14, QFont.Bold))
        title_label.setStyleSheet("color: #000000; margin: 5px 0 10px 0;")
        
        logo_label = QLabel()
        if os.path.exists(config.LOGO_PATH):
            pixmap = QPixmap(config.LOGO_PATH)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaledToHeight(50, mode=1))
        else:
            logo_label.setText("[ЛОГОТИП]")
            
        from PyQt5.QtWidgets import QHBoxLayout
        header_layout = QHBoxLayout()
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.ui.lbl_fio)
        header_layout.addWidget(self.ui.btn_logout)
        
        main_layout = self.ui.main_layout
        main_layout.insertLayout(0, header_layout)
        main_layout.insertWidget(1, title_label)
        
    def _setup_role_visibility(self):
        role = self.main_window.current_role
        self.ui.lbl_fio.setText(self.main_window.current_fio if self.main_window.current_fio != "Гость" else "")
        self.ui.lbl_fio.setVisible(role != config.ROLE_GUEST)
        self.ui.btn_logout.setVisible(role != config.ROLE_GUEST)
        
        if role in [config.ROLE_GUEST, config.ROLE_CLIENT]:
            self.ui.line_search.hide()
            self.ui.combo_sort.hide()
            self.ui.combo_filter.hide()
            self.ui.btn_orders.hide()
            self.ui.btn_add_product.hide()
        else:
            self._load_suppliers_filter()
            
        if role == config.ROLE_MANAGER:
            self.ui.btn_add_product.hide()
            
        self.ui.btn_orders.setText("Просмотреть заказы")
        
    def _load_suppliers_filter(self):
        self.ui.combo_filter.clear()
        self.ui.combo_filter.addItem("Все поставщики")
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT supplier_name FROM suppliers ORDER BY supplier_name")
            for row in cur.fetchall():
                self.ui.combo_filter.addItem(row["supplier_name"])
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "⚠️ Ошибка", f"Не удалось загрузить поставщиков: {e}")
            
    def _load_products(self):
        self.ui.list_products.clear()
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            query = """SELECT p.*, c.category_name, m.manufacturer_name, s.supplier_name
                       FROM products p
                       LEFT JOIN categories c ON p.category_id = c.id_category
                       LEFT JOIN manufacturers m ON p.manufacturer_id = m.id_manufacturer
                       LEFT JOIN suppliers s ON p.supplier_id = s.id_supplier
                       ORDER BY p.name"""
            cur.execute(query)
            products = cur.fetchall()
            conn.close()
            
            for prod in products:
                item = QListWidgetItem()
                price_html = f"{prod['price']:.2f} ₽"
                if prod['discount'] and prod['discount'] > 0:
                    final = prod['price'] * (1 - prod['discount'] / 100)
                    price_html = f"<s style='color:red'>{prod['price']:.2f} ₽</s> <b style='color:black'>{final:.2f} ₽</b>"
                    
                photo_name = prod['photo_path'] or 'picture.png'
                card = (f"<b>{prod['name']}</b><br/>"
                        f"<small>Категория: {prod['category_name']} | Производитель: {prod['manufacturer_name']} | Поставщик: {prod['supplier_name']}</small><br/>"
                        f"<small>Описание: {prod['description'][:70]}...</small><br/>"
                        f"<b>Цена: {price_html}</b> | Скидка: {prod['discount']}% | Остаток: {prod['qty']} {prod['unit']}<br/>"
                        f"<small>Фото: {photo_name}</small>")
                item.setText(card)
                
                if prod['discount'] and prod['discount'] > config.DISCOUNT_THRESHOLD:
                    item.setBackground(config.COLOR_DISCOUNT_HIGH)
                elif prod['qty'] == 0:
                    item.setBackground(config.COLOR_NO_STOCK)
                    
                self.ui.list_products.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка загрузки", f"Не удалось загрузить товары: {e}")
            
    def _connect_signals(self):
        self.ui.line_search.textChanged.connect(self._apply_filters)
        self.ui.combo_sort.currentTextChanged.connect(self._apply_filters)
        self.ui.combo_filter.currentTextChanged.connect(self._apply_filters)
        self.ui.btn_orders.clicked.connect(self._show_orders)
        self.ui.btn_add_product.clicked.connect(self._add_product)
        self.ui.btn_logout.clicked.connect(self.main_window.reset_session)
        if self.main_window.current_role == config.ROLE_ADMIN:
            self.ui.list_products.itemDoubleClicked.connect(self._edit_product)
            
    def _apply_filters(self):
        search = self.ui.line_search.text().lower()
        sort_idx = self.ui.combo_sort.currentIndex()
        supplier = self.ui.combo_filter.currentText()
        
        visible_items = []
        for i in range(self.ui.list_products.count()):
            item = self.ui.list_products.item(i)
            txt = item.text().lower()
            if search and search not in txt: continue
            if supplier != "Все поставщики" and supplier not in txt: continue
            visible_items.append(item)
            
        self.ui.list_products.clear()
        for it in visible_items:
            self.ui.list_products.addItem(it)
            
    def _show_orders(self):
        from pages.orders_page import OrdersPage
        self.main_window.switch_to(OrdersPage(self.main_window))
        
    def _add_product(self):
        if self.edit_form_open:
            QMessageBox.warning(self, "⚠️ Ограничение", "Форма редактирования уже открыта. Закройте её, чтобы создать новую.")
            return
        self.edit_form_open = True
        from pages.product_edit_form import ProductEditForm
        form = ProductEditForm(self.main_window, product_id=None)
        form.form_closed.connect(self._on_form_closed)
        self.main_window.switch_to(form)
        
    def _edit_product(self, item):
        if self.edit_form_open:
            QMessageBox.warning(self, "⚠️ Ограничение", "Форма редактирования уже открыта.")
            return
        self.edit_form_open = True
        from pages.product_edit_form import ProductEditForm
        form = ProductEditForm(self.main_window, product_id=None)
        form.form_closed.connect(self._on_form_closed)
        self.main_window.switch_to(form)
        
    def _on_form_closed(self):
        self.edit_form_open = False
        self._load_products()
