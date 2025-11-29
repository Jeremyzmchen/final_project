"""
游戏配置文件
"""

# 窗口设置
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
FPS = 60
WINDOW_TITLE = "Lost & Found Office"

# 颜色
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (200, 200, 200)
COLOR_DARK_GRAY = (100, 100, 100)
COLOR_BLUE = (100, 150, 255)
COLOR_GREEN = (100, 255, 100)
COLOR_RED = (255, 100, 100)
COLOR_YELLOW = (255, 255, 100)
COLOR_ORANGE = (255, 165, 0)

# 难度设置
DIFFICULTY_SETTINGS = {
    'chill': {'name': 'Chill', 'customer_interval': 30.0, 'time_pressure': False, 'items_per_wave': 3},
    'relax': {'name': 'Relax', 'customer_interval': 20.0, 'time_pressure': False, 'items_per_wave': 5},
    'normal': {'name': 'Normal', 'customer_interval': 15.0, 'time_pressure': True, 'items_per_wave': 7},
    'mayhem': {'name': 'Mayhem', 'customer_interval': 8.0, 'time_pressure': True, 'items_per_wave': 10}
}

# ========== 传送带设置 ==========
CONVEYOR_SPEED = 80
CONVEYOR_PAUSE_DURATION = 3.0
CONVEYOR_PAUSE_TRIGGER_Y = 470

CONVEYOR_PATH = [
    (-400, 350), (120, 350), (180, 380), (180, 580),
    (180, 580), (180, 750), (150, 800), (-400, 800),
]

CONVEYOR_PAUSE_AT_INDEX = 4
ITEM_SPAWN_INTERVAL = 20.0
ITEMS_PER_BATCH = 3
ITEM_VERTICAL_OFFSETS = [70, 0, -70]

# 区域定义
CONVEYOR_AREA = {'x': 20, 'y': 280, 'width': 240, 'height': 450}
DESK_AREA = {'x': 270, 'y': 230, 'width': 1150, 'height': 520}
STORAGE_AREA = {'x': 1200, 'y': 230, 'width': 240, 'height': 520}

# [修改] 移除旧的 CUSTOMER_DELIVERY_AREA，改用多窗口配置
# 定义 3 个顾客站位 (X坐标)
CUSTOMER_SLOTS = [500, 800, 1100]
CUSTOMER_Y = 120

# 物品设置
ITEM_SIZE = (100, 100)
ITEM_GRID_SIZE = 130

# 顾客设置
CUSTOMER_WAIT_TIME = 60.0
CUSTOMER_PATIENCE_WARNING = 20.0

# 奖惩
REWARD_CORRECT = 60
PENALTY_WRONG = -30
PENALTY_TIMEOUT = -50

# 资源路径 (保持不变)
ASSETS = {
    'bg_main': 'assets/images/background_office.png',
    'bg_menu': 'assets/images/background_menu.png',
    'customer_1': 'assets/images/customer_happy.png',
    'customer_2': 'assets/images/customer_worried.png',
    'customer_3': 'assets/images/customer_angry.png',
    'item_suitcase_orange': 'assets/images/items/suitcase_orange.png',
    'item_suitcase_black': 'assets/images/items/suitcase_black.png',
    'item_passport': 'assets/images/items/passport.png',
    'item_camera': 'assets/images/items/camera.png',
    'item_headphones': 'assets/images/items/headphones.png',
    'item_sunglasses': 'assets/images/items/sunglasses.png',
    'item_sweater': 'assets/images/items/sweater_red.png',
    'item_bottle': 'assets/images/items/water_bottle.png',
    'item_wallet': 'assets/images/items/wallet.png',
    'item_keys': 'assets/images/items/keys.png',
    'item_phone': 'assets/images/items/smartphone.png',
    'item_tablet': 'assets/images/items/tablet.png',
    'item_book': 'assets/images/items/book.png',
    'item_map': 'assets/images/items/map.png',
    'item_toy': 'assets/images/items/toy.png',
    'item_hat': 'assets/images/items/hat.png',
    'item_scarf': 'assets/images/items/scarf_blue.png',
    'item_gloves': 'assets/images/items/gloves_green.png',
    'item_umbrella': 'assets/images/items/umbrella.png',
    'item_ticket': 'assets/images/items/boarding_pass.png',
}

ITEM_DESCRIPTIONS = {
    'suitcase_orange': {'name': 'Orange Suitcase', 'size': (130, 110), 'keywords': ['orange', 'suitcase', 'large'], 'category': 'luggage'},
    'suitcase_black': {'name': 'Black Briefcase', 'size': (130, 110), 'keywords': ['black', 'briefcase', 'business'], 'category': 'luggage'},
    'passport': {'name': 'Passport', 'size': (60, 80), 'keywords': ['passport', 'red', 'document'], 'category': 'documents'},
    'ticket': {'name': 'Boarding Pass', 'size': (100, 50), 'keywords': ['ticket', 'paper'], 'category': 'documents'},
    'book': {'name': 'Book', 'size': (80, 100), 'keywords': ['book', 'reading'], 'category': 'personal'},
    'map': {'name': 'Map', 'size': (100, 80), 'keywords': ['map', 'paper'], 'category': 'personal'},
    'camera': {'name': 'Camera', 'size': (90, 70), 'keywords': ['camera', 'photo'], 'category': 'electronics'},
    'headphones': {'name': 'Headphones', 'size': (90, 90), 'keywords': ['headphones', 'music'], 'category': 'electronics'},
    'phone': {'name': 'Smartphone', 'size': (50, 90), 'keywords': ['phone', 'black'], 'category': 'electronics'},
    'tablet': {'name': 'Tablet', 'size': (100, 130), 'keywords': ['tablet', 'screen'], 'category': 'electronics'},
    'sunglasses': {'name': 'Sunglasses', 'size': (80, 40), 'keywords': ['sunglasses', 'glasses'], 'category': 'accessories'},
    'wallet': {'name': 'Wallet', 'size': (80, 60), 'keywords': ['wallet', 'leather'], 'category': 'personal'},
    'keys': {'name': 'Keys', 'size': (60, 60), 'keywords': ['keys', 'metal'], 'category': 'personal'},
    'watch': {'name': 'Watch', 'size': (50, 50), 'keywords': ['watch', 'time'], 'category': 'accessories'},
    'sweater': {'name': 'Red Sweater', 'size': (110, 100), 'keywords': ['sweater', 'red', 'clothes'], 'category': 'clothing'},
    'scarf': {'name': 'Blue Scarf', 'size': (90, 90), 'keywords': ['scarf', 'blue', 'warm'], 'category': 'clothing'},
    'gloves': {'name': 'Green Gloves', 'size': (80, 80), 'keywords': ['gloves', 'green'], 'category': 'clothing'},
    'hat': {'name': 'Hat', 'size': (100, 80), 'keywords': ['hat', 'summer'], 'category': 'clothing'},
    'bottle': {'name': 'Water Bottle', 'size': (50, 110), 'keywords': ['bottle', 'water'], 'category': 'personal'},
    'umbrella': {'name': 'Umbrella', 'size': (50, 120), 'keywords': ['umbrella', 'rain'], 'category': 'personal'},
    'toy': {'name': 'Toy', 'size': (80, 80), 'keywords': ['toy', 'play'], 'category': 'personal'},
}