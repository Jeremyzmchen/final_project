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
    'mayhem': {'name': 'Mayhem', 'customer_interval': 10.0, 'time_pressure': True, 'items_per_wave': 10}
}

# ========== 传送带设置 ==========
CONVEYOR_SPEED = 80
CONVEYOR_PAUSE_DURATION = 3.0
CONVEYOR_PAUSE_TRIGGER_Y = 470

# 传送带路径 - 超长垂直段
CONVEYOR_PATH = [
    (-400, 350),      # 0: 起点
    (120, 350),       # 1: 向右平移
    (180, 380),       # 2: 第一个转角
    (180, 580),       # 3: 向下到停留点（220px）
    (180, 580),       # 4: 停留点
    (180, 750),       # 5: 继续向下（250px）
    (150, 800),       # 6: 第二个转角
    (-400, 800),      # 7: 向左离开
]

CONVEYOR_PAUSE_AT_INDEX = 4
ITEM_SPAWN_INTERVAL = 20.0
ITEMS_PER_BATCH = 3

# 物品间距（紧凑）
ITEM_VERTICAL_OFFSETS = [70, 0, -70]

# 区域定义
CONVEYOR_AREA = {'x': 20, 'y': 280, 'width': 240, 'height': 450}
DESK_AREA = {'x': 270, 'y': 230, 'width': 1150, 'height': 520}
STORAGE_AREA = {'x': 1200, 'y': 230, 'width': 240, 'height': 520}
CUSTOMER_DELIVERY_AREA = {'x': 600, 'y': 80, 'width': 400, 'height': 150}

# 物品设置
ITEM_SIZE = (120, 120)
ITEM_GRID_SIZE = 130

# 顾客设置
CUSTOMER_WAIT_TIME = 60.0
CUSTOMER_PATIENCE_WARNING = 20.0

# 奖惩
REWARD_CORRECT = 60
PENALTY_WRONG = -30
PENALTY_TIMEOUT = -50

# 资源路径
ASSETS = {
    'bg_main': 'assets/images/background_office.png',
    'bg_menu': 'assets/images/background_menu.png',

    # 顾客图片
    'customer_1': 'assets/images/customer_happy.png',
    'customer_2': 'assets/images/customer_worried.png',
    'customer_3': 'assets/images/customer_angry.png',

    # 物品图片
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

# 物品描述
ITEM_DESCRIPTIONS = {
    'suitcase_orange': {'name': 'Orange Suitcase', 'keywords': ['orange', 'suitcase', 'large', 'wheels'], 'category': 'luggage'},
    'suitcase_black': {'name': 'Black Briefcase', 'keywords': ['black', 'briefcase', 'business', 'leather'], 'category': 'luggage'},
    'passport': {'name': 'Passport', 'keywords': ['passport', 'red', 'document', 'important'], 'category': 'documents'},
    'camera': {'name': 'Camera', 'keywords': ['camera', 'photography', 'black', 'electronic'], 'category': 'electronics'},
    'headphones': {'name': 'Headphones', 'keywords': ['headphones', 'blue', 'music', 'electronic'], 'category': 'electronics'},
    'sunglasses': {'name': 'Sunglasses', 'keywords': ['sunglasses', 'shades', 'blue frame'], 'category': 'accessories'},
    'sweater': {'name': 'Red Sweater', 'keywords': ['sweater', 'red', 'knitted', 'clothing'], 'category': 'clothing'},
    'bottle': {'name': 'Water Bottle', 'keywords': ['bottle', 'blue', 'plastic', 'water'], 'category': 'personal'},
    'scarf': {'name': 'Blue Scarf', 'keywords': ['scarf', 'blue', 'warm'], 'category': 'clothing'}
}