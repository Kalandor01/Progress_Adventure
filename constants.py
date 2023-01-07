from os import getcwd
from os.path import join

from save_file_manager import Cursor_icon

# package versions
PYTHON_MIN_VERSION = "3.11.0"
PIP_NP_MIN_VERSION = "1.23.4"
PIP_COL_MIN_VERSION = "0.4.6"
PIP_PIL_MIN_VERSION = "9.4.0"
PIP_PERLIN_MIN_VERSION = "1.12"

PIP_SFM_MIN_VERSION = "1.13.3"
PIP_RS_MIN_VERSION = "1.5.1"

# language
ENCODING = "windows-1250"

# thread names
MAIN_THREAD_NAME = "Main"
AUTO_SAVE_THREAD_NAME = "Auto saver"
MANUAL_SAVE_THREAD_NAME = "Quit manager"
TEST_THREAD_NAME = "Test"
VISUALIZER_THREAD_NAME = "Visualizer"

# paths/folders/file names
ROOT_FOLDER = getcwd()
    #saves folder
SAVES_FOLDER = "saves"
SAVES_FOLDER_PATH = join(ROOT_FOLDER, SAVES_FOLDER)
OLD_SAVE_NAME = "save*"
SAVE_EXT = "sav"
    #logs folder
LOGGING = True
LOGGING_LEVEL = 0
LOGS_FOLDER = "logs"
LOGS_FOLDER_PATH = join(ROOT_FOLDER, LOGS_FOLDER)
LOG_EXT = "log"
    #backups folder
BACKUPS_FOLDER = "backups"
BACKUPS_FOLDER_PATH = join(ROOT_FOLDER, BACKUPS_FOLDER)
OLD_BACKUP_EXT = SAVE_EXT + ".bak"
BACKUP_EXT = "zip"
    # save folder structure
SAVE_FILE_NAME_DATA = "data"
SAVE_FOLDER_NAME_CHUNKS = "chunks"

# seeds
SAVE_SEED = 87531
SETTINGS_SEED = 1

# cursor types
STANDARD_CURSOR_ICONS = Cursor_icon(selected_icon=">", selected_icon_right="",
                                    not_selected_icon=" ", not_selected_icon_right="")
DELETE_CURSOR_ICONS = Cursor_icon(selected_icon=" X", selected_icon_right="",
                                    not_selected_icon="  ", not_selected_icon_right="")

# other
ERROR_HANDLING = False
LOG_MS = False
AUTO_SAVE_INTERVAL = 20
AUTO_SAVE_DELAY = 5
FILE_ENCODING_VERSION = 2
CHUNK_SIZE = 10
CHUNK_FILE_NAME = "chunk"
CHUNK_FILE_NAME_SEP = "_"
SAVE_VERSION = "1.5.2"
DOUBLE_KEYS = [b"\xe0", b"\x00"]
TILE_NOISE_RESOLUTION = 1000000000000


# from constants import                                                       \
#     PYTHON_MIN_VERSION,                                                     \
#     PIP_NP_MIN_VERSION, PIP_COL_MIN_VERSION,                                \
#     PIP_SFM_MIN_VERSION, PIP_RS_MIN_VERSION,                                \
#     ENCODING,                                                               \
#     MAIN_THREAD_NAME, AUTO_SAVE_THREAD_NAME, MANUAL_SAVE_THREAD_NAME,       \
#     VISUALIZER_THREAD_NAME, TEST_THREAD_NAME,                               \
#     ROOT_FOLDER,                                                            \
#     SAVES_FOLDER, SAVES_FOLDER_PATH, OLD_SAVE_NAME, SAVE_EXT,               \
#     LOGGING, LOGGING_LEVEL, LOGS_FOLDER, LOGS_FOLDER_PATH, LOG_EXT,         \
#     BACKUPS_FOLDER, BACKUPS_FOLDER_PATH, OLD_BACKUP_EXT, BACKUP_EXT,        \
#     SAVE_FILE_NAME_DATA, SAVE_FOLDER_NAME_CHUNKS,                           \
#     SAVE_SEED, SETTINGS_SEED,                                               \
#     STANDARD_CURSOR_ICONS, DELETE_CURSOR_ICONS,                             \
#     ERROR_HANDLING, LOG_MS,                                                 \
#     AUTO_SAVE_INTERVAL, AUTO_SAVE_DELAY, FILE_ENCODING_VERSION, CHUNK_SIZE, \
#     CHUNK_FILE_NAME, CHUNK_FILE_NAME_SEP                                    \
#     SAVE_VERSION, DOUBLE_KEYS, TILE_NOISE_RESOLUTION
