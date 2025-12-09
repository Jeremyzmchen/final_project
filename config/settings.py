"""
Game Settings
"""

# Window setting
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
FPS = 60
WINDOW_TITLE = "Lost but Found"

# Color Dict
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (200, 200, 200)
COLOR_DARK_GRAY = (100, 100, 100)
COLOR_BLUE = (100, 150, 255)
COLOR_GREEN = (100, 255, 100)
COLOR_RED = (128, 4, 4)
COLOR_YELLOW = (255, 200, 50)
COLOR_ORANGE = (255, 165, 0)

# Font
FONT_PATH = 'assets/fonts/game_font.ttf'

SOUNDS = {
    # BGM
    'bgm_menu': 'assets/sounds/bgm_menu.ogg',
    'bgm_game': 'assets/sounds/bgm_play.mp3',
    
    # sound effects (SFX)
    'sfx_money': 'assets/sounds/sfx_money.wav',
    'sfx_deny': 'assets/sounds/sfx_deny.mp3',
    'sfx_click': 'assets/sounds/sfx_click.wav',
    'sfx_pick': 'assets/sounds/sfx_pick.wav',
    'sfx_drop': 'assets/sounds/sfx_drop.mp3',
    'sfx_spray': 'assets/sounds/sfx_spray.wav',
}

# Game parameters
# NPC setting
CUSTOMER_INTERVAL = 7.0      # NPC spawn interval
CUSTOMER_SLOTS = [750, 1050, 1350]
CUSTOMER_Y = 120    # Stop at this Y
CUSTOMER_WAIT_TIME = 25.0    # Customer wait time

# Conveyor setting
CONVEYOR_SPEED = 400
CONVEYOR_PAUSE_DURATION = 8.0
CONVEYOR_PAUSE_TRIGGER_Y = 270
CONVEYOR_CENTER_X = 140      # Set center_x
CONVEYOR_WIDTH = 180         # Set width

ITEM_SPAWN_INTERVAL = 18.0
ITEMS_PER_BATCH = 3
ITEM_VERTICAL_OFFSETS = [30, 0, -30]
CONVEYOR_PAUSE_AT_INDEX = 2

# 区域定义
# 物品被拖到这里时，属于“已整理”，会被物理引擎接管（挤开效果）。
# TODO 12.04修改替换
CONVEYOR_AREA = {'x': 40, 'y': 0, 'width': 200, 'height': 900}
DESK_AREA = {'x': 270, 'y': 350, 'width': 1200, 'height': 500}

# [新增] 小偷专用配置
THIEF_SPAWN_PROB = 0.15      # 25% 的概率生成小偷 (可以自己调)
THIEF_WAIT_TIME = 15.0       # 小偷只待 15 秒 (比普通顾客短)
THIEF_HP = 10                 # 需要点击 3 次喷雾才能赶走
THIEF_PENALTY_HIT = -200     # 被小偷得逞扣的分

# 经济系统
REWARD_CORRECT = 100
PENALTY_WRONG = -50
PENALTY_TIMEOUT = -20
PENALTY_CLICK = -10


# 资源路径 (保持不变)
ASSETS = {
    # UI
    'cursor': 'assets/images/icons/cursor.png',
    'bg_main': 'assets/images/background_game.png',
    'bg_menu': 'assets/images/background_menu.png',
    'bg_game_over': 'assets/images/background_game_over.png',
    'conveyor_belt': 'assets/images/conveyor_belt.png',
    # NPC
    'thief': 'assets/images/thief.png',
    'item_spray': 'assets/images/icons/spray.png',
    'npc_1': 'assets/images/npc_1.png',
    'npc_2': 'assets/images/npc_2.png',
    'npc_3': 'assets/images/npc_3.png',
    'npc_4': 'assets/images/npc_4.png',
    'npc_5': 'assets/images/npc_5.png',
    'npc_6': 'assets/images/npc_6.png',
    'npc_7': 'assets/images/npc_7.png',
    'npc_8': 'assets/images/npc_8.png',
    'npc_9': 'assets/images/npc_9.png',
    'npc_10': 'assets/images/npc_10.png',
    'npc_11': 'assets/images/npc_11.png',
    'npc_12': 'assets/images/npc_12.png',
    # ITEM_DOCUMENT
    'item_boarding_pass': 'assets/images/items/boarding_pass.png',
    'item_book': 'assets/images/items/book.png',
    'item_business_card': 'assets/images/items/business_card.png',
    'item_concert_ticket': 'assets/images/items/concert_ticket.png',
    'item_credit_card': 'assets/images/items/credit_card.png',
    'item_driver_license': 'assets/images/items/driver_license.png',
    'item_letter': 'assets/images/items/letter.png',
    'item_magazine': 'assets/images/items/magazine.png',
    'item_movie_ticket': 'assets/images/items/movie_ticket.png',
    'item_newspaper': 'assets/images/items/newspaper.png',
    'item_notebook': 'assets/images/items/notebook.png',
    'item_thesis': 'assets/images/items/thesis.png',
    'item_passport': 'assets/images/items/passport.png',
    'item_stamp': 'assets/images/items/stamp.png',
    'item_student_IDcard': 'assets/images/items/student_IDcard.png',
    # ITEM_DIGITAL
    'item_camera': 'assets/images/items/camera.png',
    'item_gamepad': 'assets/images/items/gamepad.png',
    'item_hard_disk': 'assets/images/items/hard_disk.png',
    'item_headset': 'assets/images/items/headset.png',
    'item_headphones': 'assets/images/items/headphones.png',
    'item_ipad': 'assets/images/items/ipad.png',
    'item_JBL': 'assets/images/items/JBL.png',
    'item_keyboard': 'assets/images/items/keyboard.png',
    'item_mouse': 'assets/images/items/mouse.png',
    'item_phone': 'assets/images/items/phone.png',
    'item_power_bank': 'assets/images/items/power_bank.png',
    'item_UAV': 'assets/images/items/UAV.png',
    'item_USB': 'assets/images/items/USB.png',
    'item_watch': 'assets/images/items/watch.png',
    # ITEM_CLOTHES
    'item_trousers': 'assets/images/items/trousers.png',
    'item_woollen_gloves': 'assets/images/items/woollen_gloves.png',
    'item_overalls': 'assets/images/items/overalls.png',
    'item_white_sweater': 'assets/images/items/white_sweater.png',
    'item_scarf': 'assets/images/items/scarf.png',
    'item_hat': 'assets/images/items/hat.png',
}

ITEM_DESCRIPTIONS = {
    'boarding_pass': {'name': 'Boarding Pass', 'size': (90, 40), 'keywords': ['blue', 'airport', 'travel'], 'category': 'pers'},
    'book': {'name': 'Book', 'size': (80, 110), 'keywords': ['blue', 'read', 'school'], 'category': 'docs'},
    'business_card': {'name': 'Business Card', 'size': (70, 45), 'keywords': ['white', 'card', 'office'], 'category': 'pers'},
    'concert_ticket': {'name': 'Concert Ticket', 'size': (70, 35), 'keywords': ['orange', 'music', 'broadway'], 'category': 'docs'},
    'credit_card': {'name': 'Credit Card', 'size': (70, 45), 'keywords': ['bank', 'money', 'BOA'], 'category': 'pers'},
    'driver_license': {'name': 'Driver License', 'size': (70, 45), 'keywords': ['car', 'driving', 'permit'], 'category': 'pers'},
    'letter': {'name': 'Letter', 'size': (80, 80), 'keywords': ['mail', 'envelope', 'postal'], 'category': 'docs'},
    'magazine': {'name': 'Magazine', 'size': (135, 140), 'keywords': ['VOGUE', 'yellow', 'fashion'], 'category': 'docs'},
    'movie_ticket': {'name': 'Movie Ticket', 'size': (70, 35), 'keywords': ['film', 'cinema', 'Zootopia'], 'category': 'docs'},
    'newspaper': {'name': 'Newspaper', 'size': (120, 95), 'keywords': ['news', 'Times', 'politic'], 'category': 'docs'},
    'notebook': {'name': 'Notebook', 'size': (75, 90), 'keywords': ['study', 'class', 'review'], 'category': 'docs'},
    'thesis': {'name': 'Thesis', 'size': (75, 90), 'keywords': ['paper', 'SCI', 'grad'], 'category': 'docs'},
    'passport': {'name': 'Passport', 'size': (55, 70), 'keywords': ['travel', 'customs', 'visa'], 'category': 'pers'},
    'stamp': {'name': 'Stamp', 'size': (35, 35), 'keywords': ['mail', 'letter', 'purple'], 'category': 'docs'},
    'student_IDcard': {'name': 'Student IDcard', 'size': (70, 45), 'keywords': ['ID', 'student', 'card'], 'category': 'pers'},
    'camera': {'name': 'Camera', 'size': (90, 67), 'keywords': ['photo', 'Nikon', 'lens'], 'category': 'digit'},
    'gamepad': {'name': 'Gamepad', 'size': (105, 65), 'keywords': ['game', 'play', 'steam'], 'category': 'digit'},
    'hard_disk': {'name': 'Hard Disk', 'size': (90, 70), 'keywords': ['data', 'computer', 'store'], 'category': 'digit'},
    'headset': {'name': 'Headset', 'size': (60, 65), 'keywords': ['Apple', 'white', 'ear'], 'category': 'digit'},
    'headphones': {'name': 'Headphones', 'size': (155, 155), 'keywords': ['Beats', 'blue', 'ear'], 'category': 'digit'},
    'ipad': {'name': 'Ipad', 'size': (75, 100), 'keywords': ['Apple', 'notes', 'play'], 'category': 'digit'},
    'JBL': {'name': 'JBL', 'size': (125, 50), 'keywords': ['stereo', 'music', 'blue'], 'category': 'digit'},
    'keyboard': {'name': 'Keyboard', 'size': (165, 100), 'keywords': ['typewriter', 'Cherry', 'comp'], 'category': 'digit'},
    'mouse': {'name': 'Mouse', 'size': (50, 80), 'keywords': ['click', 'Mickey', 'small'], 'category': 'digit'},
    'phone': {'name': 'Phone', 'size': (50, 90), 'keywords': ['Apple', '17pro', 'tele'], 'category': 'digit'},
    'power_bank': {'name': 'Power Bank', 'size': (90, 70), 'keywords': ['travel', 'power', 'electric'], 'category': 'digit'},
    'UAV': {'name': 'UAV', 'size': (130, 130), 'keywords': ['DJI', 'drone', 'camera'], 'category': 'digit'},
    'USB': {'name': 'USB', 'size': (40, 25), 'keywords': ['data', 'store', 'small'], 'category': 'digit'},
    'trousers': {'name': 'Trousers', 'size': (125, 140), 'keywords': ['khaki', 'uniform', 'style'], 'category': 'clothes'},
    'woollen_gloves': {'name': 'Woollen Gloves', 'size': (115, 80), 'keywords': ['wool', 'warm', 'winter'], 'category': 'clothes'},
    'overalls': {'name': 'Overalls', 'size': (125, 125), 'keywords': ['denim', 'blue', 'style'], 'category': 'clothes'},
    'white_sweater': {'name': 'White Sweater', 'size': (125, 125), 'keywords': ['wool', 'winter', 'white'], 'category': 'clothes'},
    'scarf': {'name': 'Scarf', 'size': (115, 80), 'keywords': ['wool', 'warm', 'neck'], 'category': 'clothes'},
    'hat': {'name': 'Hat', 'size': (150, 150), 'keywords': ['summer', 'head', 'sunshine'], 'category': 'clothes'},
}