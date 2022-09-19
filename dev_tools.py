import json
import os

import colorama
import classes as cl
import tools as ts
from tools import BACKUP_EXT, BACKUPS_FOLDER_PATH, sfm
from tools import MAIN_THREAD_NAME, TEST_THREAD_NAME
from tools import SAVES_FOLDER_PATH, SAVE_SEED, SAVE_EXT
from tools import ENCODING, SETTINGS_ENCODE_SEED, FILE_ENCODING_VERSION
from tools import C_F_GREEN, C_F_RED, SAVE_VERSION

def decode_save_file(save_name:str, save_name_pre=SAVES_FOLDER_PATH):
    """
    Decodes a save file into a normal json.
    """
    try:
        save_data = sfm.decode_save(SAVE_SEED, os.path.join(save_name_pre, save_name), SAVE_EXT, ENCODING)
    except FileNotFoundError:
        print("decode_save_file: FILE NOT FOUND!")
    else:
        f = open(f'{save_name}.decoded.json', "w")
        for line in save_data:
            f.write(line + "\n")
        f.close()


def encode_save_file(save_name:str, pre_save_name=SAVES_FOLDER_PATH):
    """
    Encodes a json file into a .sav file.
    """
    try:
        f = open(f'{save_name}.decoded.json', "r")
        save_data = f.readlines()
        f.close()
        save_data_new = []
        for line in save_data:
            save_data_new.append(line.replace("\n", ""))
    except FileNotFoundError:
        print("encode_save_file: FILE NOT FOUND!")
    else:
        sfm.encode_save(save_data_new, SAVE_SEED, os.path.join(pre_save_name, save_name), SAVE_EXT, ENCODING, FILE_ENCODING_VERSION)


def recompile_save_file(save_name:str, new_save_name:str, pre_save_name=SAVES_FOLDER_PATH, new_pre_save_name=SAVES_FOLDER_PATH, save_ext=SAVE_EXT, new_save_ext=SAVE_EXT):
    """
    Recompiles a save file to a different name/number.
    """
    if new_save_name == None:
        new_save_name = save_name
    try:
        save_data = sfm.decode_save(SAVE_SEED, os.path.join(pre_save_name, save_name), save_ext, ENCODING)
    except FileNotFoundError:
        print("recompile_save_file: FILE NOT FOUND!")
        return False
    else:
        sfm.encode_save(save_data, os.path.join(new_pre_save_name, new_save_name), new_save_ext, ENCODING, FILE_ENCODING_VERSION)
        return True




# def file_reader(save_seed:int=SAVE_SEED, save_ext:str=BACKUP_EXT, dir_name:str=BACKUPS_FOLDER_PATH, decode_until:int=1):
#     """
#     sfm.file_reader but for backups
#     """
#     from os import path, listdir

#     # get existing file numbers
#     file_names = listdir(dir_name)
#     existing_files = []
#     for name in file_names:
#         if path.isfile(path.join(dir_name, name)) and name.find(save_ext) and name.find(save_name.replace("*", "")):
#             try: file_number = int(name.replace(f".{save_ext}", "").split(save_name.replace("*", ""))[1])
#             except ValueError: continue
#             existing_files.append([name, file_number])
#     existing_files.sort()

#     file_data = []
#     for files in existing_files:
#         try:
#             try:
#                 data = sfm.decode_save(files[1], path.join(dir_name, files[0]), "", decode_until=decode_until)
#             except ValueError:
#                 data = -1
#         except FileNotFoundError: print("not found " + str(files))
#         else:
#             file_data.append([files[0].replace("." + BACKUP_EXT, ""), data])
#     return file_data

def get_saves_data():
    """
    main.get_saves_data but for backups
    """
    ts.recreate_backups_folder()
    ts.recreate_saves_folder()
    # read saves
    datas = sfm.file_reader_blank(SAVE_SEED, BACKUPS_FOLDER_PATH)
    # process file data
    datas_processed = []
    for data in datas:
        if data[1] == -1:
            ts.press_key(f"\"{data[0]}\" is corrupted!")
        else:
            try:
                data[1] = json.loads(data[1][0])
                data_processed = ""
                data_processed += f"\"{data[0]}\": {data[1]['player_name']}\n"
                last_access = data[1]["last_access"]
                data_processed += f"Last opened: {ts.make_date(last_access, '.')} {ts.make_time(last_access[3:])}"
                # check version
                try: save_version = data[1]["save_version"]
                except KeyError: save_version = 0.0
                data_processed += ts.text_c(f" v.{save_version}", (C_F_GREEN if save_version == SAVE_VERSION else C_F_RED))
                datas_processed.append([data[0], data_processed])
            except (TypeError, IndexError):
                ts.press_key(f"\"{data[0]}\" could not be parsed!")
    return datas_processed

def load_backup_menu():
    """
    W.I.P. Backup loading menu.
    """
    colorama.init()
    files_data = get_saves_data()
    while True:
        # get data from file_data
        list_data = []
        for data in files_data:
            list_data.append(data[1])
            list_data.append(None)
        option = sfm.UI_list_s(list_data, " Backup loading", True, True, exclude_none=True).display()
        # load
        if option == -1:
            break
        else:
            file_name = str(files_data[int(option)][0])
            if recompile_save_file(file_name, file_name, os.path.join(BACKUPS_FOLDER_PATH, file_name), os.path.join(SAVES_FOLDER_PATH, file_name), BACKUP_EXT, SAVE_EXT):
                input("\n" + file_name + " loaded!")
    colorama.deinit()



# thread_1 = threading.Thread(target="function", name="Thread name", args=["argument list"])
# thread_1.start()
# merge main and started thread 1?
# thread_1.join()

class Self_Checks:
    def __init__(self):
        ts.threading.current_thread().name = TEST_THREAD_NAME
        ts.begin_log()
        self.initialization(False)
        self.settings_checks(False)


    def initialization(self, seprate=True):
        if seprate:
            ts.begin_log()
        print(end="Initialization check...")
        ts.log_info("Initialization check", "Running...")

        import sys
        from tools import colorama

        try:
            ts.check_package_versions()
            colorama.init()

            # GLOBAL VARIABLES
            GOOD_PACKAGES = True
            SETTINGS = cl.Settings(ts.settings_manager("auto_save"), ts.settings_manager("keybinds"))
            SETTINGS.save_keybind_mapping()
            SAVE_DATA = cl.Save_data
            GLOBALS = cl.Globals(False, False, False)
        except:
            print("Crashed")
            ts.log_info("Initialization check", "Preloading crahed: " + str(sys.exc_info()), "FAIL")
        else:
            print("Passed")
            ts.log_info("Initialization check", "Passed", "PASS")
    

    def settings_checks(self, seprate=True):
        if seprate:
            ts.begin_log()
        good = False
        print(end="Settings checks...")
        ts.log_info("Settings checks", "Running...")
        settings = cl.Settings(ts.settings_manager("auto_save"), ts.settings_manager("keybinds"))
        settings.save_keybind_mapping()
        if settings.auto_save == True or settings.auto_save == False:
            if settings.DOUBLE_KEYS == ts.DOUBLE_KEYS and type(settings.keybinds) == dict:
                print("Passed")
                ts.log_info("Settings checks", "Passed", "PASS")
                good = True
        if not good:
            print("Failed")
            ts.log_info("Settings checks", "Failed", "FAIL")


# Self_Checks()