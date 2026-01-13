"""
PyVenture: The Code Warrior - Settings Module
Game configuration and constants.
"""

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "PyVenture: The Code Warrior"

# =============================================================================
# GRID SETTINGS
# =============================================================================
TILE_SIZE = 64
GRID_COLS = 12  # Game area columns
GRID_ROWS = 9   # Game area rows
GAME_AREA_WIDTH = TILE_SIZE * GRID_COLS   # 768px
GAME_AREA_HEIGHT = TILE_SIZE * GRID_ROWS  # 576px
GAME_AREA_X = 40
GAME_AREA_Y = 40

# =============================================================================
# CONSOLE SETTINGS
# =============================================================================
CONSOLE_X = GAME_AREA_X + GAME_AREA_WIDTH + 40
CONSOLE_Y = GAME_AREA_Y
CONSOLE_WIDTH = SCREEN_WIDTH - CONSOLE_X - 40
CONSOLE_HEIGHT = GAME_AREA_HEIGHT
CONSOLE_PADDING = 15
CONSOLE_MAX_HISTORY = 50
CONSOLE_MAX_OUTPUT_LINES = 15

# =============================================================================
# COLORS - Premium Color Palette
# =============================================================================
# Background Colors
COLOR_BG_DARK = (15, 15, 25)
COLOR_BG_MEDIUM = (25, 28, 40)
COLOR_BG_LIGHT = (35, 40, 55)

# Accent Colors
COLOR_PRIMARY = (99, 102, 241)      # Indigo
COLOR_SECONDARY = (139, 92, 246)    # Purple
COLOR_ACCENT = (34, 211, 238)       # Cyan
COLOR_SUCCESS = (52, 211, 153)      # Emerald
COLOR_WARNING = (251, 191, 36)      # Amber
COLOR_ERROR = (248, 113, 113)       # Red

# Text Colors
COLOR_TEXT_PRIMARY = (248, 250, 252)
COLOR_TEXT_SECONDARY = (148, 163, 184)
COLOR_TEXT_MUTED = (100, 116, 139)

# Grid Colors
COLOR_GRID_LINE = (45, 50, 70)
COLOR_GRID_ACCENT = (55, 60, 85)

# Console Colors
COLOR_CONSOLE_BG = (20, 22, 35, 230)  # Semi-transparent
COLOR_CONSOLE_BORDER = (60, 65, 90)
COLOR_CONSOLE_INPUT_BG = (30, 35, 50)
COLOR_CONSOLE_PROMPT = (34, 211, 238)
COLOR_CONSOLE_CURSOR = (99, 102, 241)

# Player Colors
COLOR_PLAYER = (99, 102, 241)
COLOR_PLAYER_GLOW = (139, 92, 246)

# =============================================================================
# PLAYER SETTINGS
# =============================================================================
PLAYER_START_COL = 5
PLAYER_START_ROW = 4
PLAYER_MOVE_SPEED = 8  # Pixels per frame during animation

# =============================================================================
# FONT SETTINGS
# =============================================================================
FONT_NAME = None  # Use pygame default, or specify a path
FONT_SIZE_LARGE = 32
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 18
FONT_SIZE_CONSOLE = 20
FONT_SIZE_TINY = 14

# =============================================================================
# ANIMATION SETTINGS
# =============================================================================
CURSOR_BLINK_INTERVAL = 500  # milliseconds
PLAYER_ANIMATION_FRAMES = 8  # frames for smooth movement

# =============================================================================
# VALID COMMANDS - For educational feedback
# =============================================================================
VALID_HERO_METHODS = [
    "move_right",
    "move_left", 
    "move_up",
    "move_down",
    "jump",
    "attack",
    "defend",
    "say",
    "spin",
    "dance",
    "collect",
]

# Similar method suggestions for typo correction
METHOD_SUGGESTIONS = {
    "moveright": "move_right",
    "moveleft": "move_left",
    "moveup": "move_up",
    "movedown": "move_down",
    "move_rigth": "move_right",
    "move_rigt": "move_right",
    "move_leftt": "move_left",
    "move_u": "move_up",
    "move_d": "move_down",
    "right": "move_right",
    "left": "move_left",
    "up": "move_up",
    "down": "move_down",
    "spinn": "spin",
    "dans": "dance",
    "dansce": "dance",
}

