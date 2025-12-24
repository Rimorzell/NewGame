"""
Frozen Signal - Game Constants and Configuration
A survival horror game inspired by Signalis
"""

# Display settings
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
RENDER_WIDTH = 320
RENDER_HEIGHT = 240
FPS = 60
TITLE = "FROZEN SIGNAL"

# Tile settings
TILE_SIZE = 16
CHUNK_SIZE = 16

# Player settings
PLAYER_SPEED = 1.5
PLAYER_RUN_SPEED = 2.5
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_SANITY = 100
PLAYER_MAX_WARMTH = 100
SANITY_DRAIN_RATE = 0.02
COLD_DRAIN_RATE = 0.05
COLD_DAMAGE_THRESHOLD = 20
COLD_DAMAGE_RATE = 0.1

# Inventory settings
INVENTORY_SLOTS = 6
MAX_STACK_SIZE = 5

# Combat settings
MELEE_DAMAGE = 25
MELEE_RANGE = 20
PISTOL_DAMAGE = 40
PISTOL_RANGE = 150

# Enemy settings
ENEMY_DETECTION_RANGE = 80
ENEMY_ATTACK_RANGE = 16
ENEMY_PATROL_SPEED = 0.5
ENEMY_CHASE_SPEED = 1.2

# Color Palette - Cold, sterile Signalis-inspired
class Colors:
    # Primary palette
    BLACK = (8, 8, 12)
    DARK_BLUE = (15, 20, 35)
    DEEP_BLUE = (25, 35, 60)
    ICE_BLUE = (45, 65, 95)
    FROST = (120, 145, 175)
    STERILE_WHITE = (200, 210, 220)
    PURE_WHITE = (240, 245, 250)

    # Warning colors
    BLOOD_RED = (140, 25, 30)
    WARNING_RED = (180, 45, 50)
    ALARM_RED = (220, 60, 65)

    # Amber/warmth
    AMBER_DARK = (120, 70, 20)
    AMBER = (180, 120, 40)
    AMBER_LIGHT = (220, 170, 80)

    # UI colors
    UI_BACKGROUND = (12, 15, 25)
    UI_BORDER = (60, 80, 110)
    UI_TEXT = (180, 195, 210)
    UI_HIGHLIGHT = (100, 140, 180)
    UI_DANGER = (180, 50, 50)

    # Environmental
    RUST = (100, 55, 40)
    FROZEN_FLESH = (85, 95, 110)
    ORGANIC_DARK = (35, 30, 40)

    # Transparency
    SHADOW = (0, 0, 0, 180)
    FOG = (20, 30, 50, 100)

# Game states
class GameState:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    DIALOGUE = "dialogue"
    EXAMINING = "examining"
    CUTSCENE = "cutscene"
    GAME_OVER = "game_over"
    ENDING = "ending"

# Item types
class ItemType:
    KEY = "key"
    WEAPON = "weapon"
    AMMO = "ammo"
    HEALING = "healing"
    DOCUMENT = "document"
    AUDIO_LOG = "audio_log"
    PUZZLE = "puzzle"
    WARMTH = "warmth"

# Direction constants
class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)

# Layer ordering
class Layer:
    FLOOR = 0
    FLOOR_DECOR = 1
    WALLS = 2
    OBJECTS = 3
    ENTITIES = 4
    PLAYER = 5
    EFFECTS = 6
    UI = 7

# Sound channels
class SoundChannel:
    AMBIENT = 0
    EFFECTS = 1
    VOICE = 2
    MUSIC = 3
    UI = 4

# Room types
class RoomType:
    CORRIDOR = "corridor"
    LAB = "lab"
    STORAGE = "storage"
    OFFICE = "office"
    MEDICAL = "medical"
    QUARTERS = "quarters"
    REACTOR = "reactor"
    COMMUNICATIONS = "communications"
    DEEP_EXCAVATION = "deep_excavation"

# Ending flags
class EndingFlag:
    DISCOVERED_SIGNAL = "discovered_signal"
    FREED_SUBJECTS = "freed_subjects"
    DESTROYED_TRANSMITTER = "destroyed_transmitter"
    READ_ALL_LOGS = "read_all_logs"
    SAVED_SURVIVOR = "saved_survivor"
    ESCAPED = "escaped"
    EMBRACED = "embraced"
