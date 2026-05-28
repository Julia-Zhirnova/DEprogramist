import os
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt
from PyQt5 import uic
import config, db_manager

class ProductsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = uic.loadUi(os.path.join(config.UI_DIR, "products.ui"), self)
        self.products_data = []
        self.edit_form_open = False
        
        self._setup_header()
        self._setup_role_visibility()
        self._connect_signals()
        self._load_products()

    def _setup_header(self):
        title = QLabel("Каталог товаров")
        title.setFont(QFont(config.FONT_FAMILY, 14, QFont.Bold))
        title.setStyleSheet("color: #000000; margin: 5px 0 10px 0;")
        
        logo = QLabel()
        if os.path.exists(config.LOGO_PATH):
            px = QPixmap(config.LOGO_PATH)
            if not px.isNull(): logo.setPixmap(px.scaledToHeight(50, mode=1))
        else: logo.setText("[ЛОГОТИП]")
            
        from PyQt5.QtWidgets import QHBoxLayout
        lay = QHBoxLayout()
        lay.addWidget(logo); lay.addStretch()
        lay.addWidget(self.ui.lbl_fio); lay.addWidget(self.ui.btn_logout)
        self.ui.main_layout.insertLayout(0, lay)
        self.ui.main_layout.insertWidget(1, title)

    def _setup_role_visibility(self):
        self.ui.lbl_fio.setText(self.main_window.current_fio if self.main_window.current_fio != "Гость" else "")
        self.ui.lbl_fio.setVisible(self.main_window.current_fio != "Гость")
        self.ui.btn_logout.setVisible(True)
        
        if self.main_window.current_role in [config.ROLE_GUEST, config.ROLE_CLIENT]:
            for w in [self.ui.line_search, self.ui.combo_sort, self.ui.combo_filter, self.ui.btn_orders, self.ui.btn_add_product]: w.hide()
        else:
            self._load_suppliers_filter()
            
        if self.main_window.current_role == config.ROLE_MANAGER: self.ui.btn_add_product.hide()
        self.ui.btn_orders.setText("Просмотреть заказы")

    def _load_suppliers_filter(self):
        self.ui.combo_filter.clear()
        self.ui.combo_filter.addItem("Все поставщики")
        try:
            conn = db_manager.get_connection()
            for r in conn.cursor().execute("SELECT supplier_name FROM suppliers ORDER BY supplier_name").fetchall():
                self.ui.combo_filter.addItem(r["supplier_name"])
            conn.close()
        except Exception as e:
            print(f"⚠️ Фильтр поставщиков: {e}")

    def _load_products(self):
        try:
            conn = db_manager.get_connection()
            cur = conn.cursor()
            cur.execute('''SELECT p.*, c.category_name, m.manufacturer_name, s.supplier_name
                           FROM products p
                           LEFT JOIN categories c ON p.category_id = c.id_category
                           LEFT JOIN manufacturers m ON p.manufacturer_id = m.id_manufacturer
                           LEFT JOIN suppliers s ON p.supplier_id = s.id_supplier
                           ORDER BY p.name''')
            self.products_data = [db_manager.row_to_dict(r) for r in cur.fetchall()]
            conn.close()
            if not self.products_data:
                print("⚠️ База вернула 0 товаров. Проверьте shoe_store.db и наличие записей.")
        except Exception as e:
            print(f"❌ Ошибка загрузки товаров: {e}")
            QMessageBox.critical(self, "❌ Ошибка БД", f"Не удалось загрузить товары: {e}")
            self.products_data = []
        self._render_products()

    def _render_products(self, data=None):
        items = data if data is not None else self.products_data
        self.ui.list_products.clear()
        
        for p in items:
            it = QListWidgetItem()
            price = f"{p['price']:.2f} ₽"
            if p.get('discount') and p['discount'] > 0:
                final = p['price'] * (1 - p['discount'] / 100)
                price = f"<s style='color:red'>{p['price']:.2f} ₽</s> <b style='color:black'>{final:.2f} ₽</b>"
                
            photo = p.get('photo_path') or 'picture.png'
            html = (f"<b>{p['name']}</b><br/>"
                    f"<small>Категория: {p.get('category_name','-')} | Производитель: {p.get('manufacturer_name','-')} | Поставщик: {p.get('supplier_name','-')}</small><br/>"
                    f"<small>Описание: {str(p.get('description',''))[:70]}...</small><br/>"
                    f"<b>Цена: {price}</b> | Скидка: {p.get('discount',0)}% | Остаток: {p.get('quantity',0)} {p.get('unit','шт.')}<br/>"
                    f"<small>Фото: {photo}</small>")
            it.setText(html)
            
            if p.get('discount') and p['discount'] > config.DISCOUNT_THRESHOLD:
                it.setBackground(QColor(config.COLOR_DISCOUNT_HIGH))
            elif p.get('quantity') == 0:
                it.setBackground(QColor(config.COLOR_NO_STOCK))
            self.ui.list_products.addItem(it)

    def _apply_filters(self):
        search = self.ui.line_search.text().lower()
        sort_idx = self.ui.combo_sort.currentIndex()
        supplier = self.ui.combo_filter.currentText()
        
        filtered = []
        for p in self.products_data:
            txt = f"{p.get('name','')} {p.get('description','')} {p.get('category_name','')} {p.get('manufacturer_name','')} {p.get('supplier_name','')} {p.get('unit','')}".lower()
            if search and search not in txt: continue
            if supplier != "Все поставщики" and supplier != p.get('supplier_name'): continue
            filtered.append(p)
            
        if sort_idx == 1: filtered.sort(key=lambda x: x.get('quantity', 0))
        elif sort_idx == 2: filtered.sort(key=lambda x: -x.get('quantity', 0))
        self._render_products(filtered)

    def _connect_signals(self):
        self.ui.line_search.textChanged.connect(self._apply_filters)
        self.ui.combo_sort.currentTextChanged.connect(self._apply_filters)
        self.ui.combo_filter.currentTextChanged.connect(self._apply_filters)
        self.ui.btn_orders.clicked.connect(lambda: self._show_page("orders"))
        self.ui.btn_add_product.clicked.connect(lambda: self._show_page("add_product"))
        self.ui.btn_logout.clicked.connect(self.main_window.reset_session)
        if self.main_window.current_role == config.ROLE_ADMIN:
            self.ui.list_products.itemDoubleClicked.connect(lambda: self._show_page("edit_product"))

    def _show_page(self, page):
        if page in ["add_product", "edit_product"] and self.edit_form_open:
            QMessageBox.warning(self, "⚠️ Ограничение", "Форма редактирования уже открыта.")
            return
        self.edit_form_open = True
        from pages.product_edit_form import ProductEditForm
        form = ProductEditForm(self.main_window, product_id=None)
        form.form_closed.connect(self._on_form_closed)
        self.main_window.stack.addWidget(form)
        self.main_window.stack.setCurrentWidget(form)
        if page == "orders":
            from pages.orders_page import OrdersPage
            self.main_window.stack.addWidget(OrdersPage(self.main_window))
            self.main_window.stack.setCurrentWidget(self.main_window.stack.widget(self.main_window.stack.count()-1))

    def _on_form_closed(self):
        self.edit_form_open = False
        self._load_products()
        self.main_window.stack.setCurrentWidget(self)
