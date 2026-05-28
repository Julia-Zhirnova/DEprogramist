import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "shoe_store.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PHOTOS_DIR = os.path.join(ASSETS_DIR, "photos")
UI_DIR = os.path.join(BASE_DIR, "ui")

os.makedirs(PHOTOS_DIR, exist_ok=True)

ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
PLACEHOLDER_PATH = os.path.join(ASSETS_DIR, "picture.png")

COLOR_BG_MAIN = "#FFFFFF"
COLOR_BG_ADD = "#7FFF00"
COLOR_ACCENT = "#00FA9A"
COLOR_DISCOUNT_HIGH = "#2E8B57"
COLOR_NO_STOCK = "#ADD8E6"
COLOR_STRIKETHROUGH = "#FF0000"
COLOR_FINAL_PRICE = "#000000"

FONT_FAMILY = "Times New Roman"
FONT_SIZE = 10

ROLE_GUEST = 0
ROLE_CLIENT = 3
ROLE_MANAGER = 2
ROLE_ADMIN = 1

PHOTO_MAX_WIDTH = 300
PHOTO_MAX_HEIGHT = 200
DISCOUNT_THRESHOLD = 15.0
