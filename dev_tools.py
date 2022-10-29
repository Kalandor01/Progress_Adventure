import json
import os

from utils import Color
import utils as u
import tools as ts
from tools import OLD_BACKUP_EXT, BACKUPS_FOLDER_PATH, sfm
from tools import TEST_THREAD_NAME
from tools import SAVES_FOLDER_PATH, SAVE_SEED, SAVE_EXT
from tools import ENCODING, FILE_ENCODING_VERSION
from tools import SAVE_VERSION
import data_manager as dm

def decode_save_file(save_name:str, save_name_pre=SAVES_FOLDER_PATH, save_num=SAVE_SEED, save_ext=SAVE_EXT):
    """
    Decodes a save file into a normal json.
    """
    try:
        save_data = sfm.decode_save(save_num, os.path.join(save_name_pre, save_name), save_ext, ENCODING)
    except FileNotFoundError:
        print(f"decode_save_file: FILE {save_name} NOT FOUND!")
    else:
        with open(f'{save_name}.decoded.json', "w") as f:
            for line in save_data:
                f.write(line + "\n")


def encode_save_file(save_name:str, pre_save_name=SAVES_FOLDER_PATH, save_num=SAVE_SEED, save_ext=SAVE_EXT):
    """
    Encodes a json file into a .sav file.
    """
    try:
        with open(f'{save_name}.decoded.json', "r") as f:
            save_data = f.readlines()
        save_data_new = []
        for line in save_data:
            save_data_new.append(line.replace("\n", ""))
    except FileNotFoundError:
        print(f"encode_save_file: FILE {save_name} NOT FOUND!")
    else:
        sfm.encode_save(save_data_new, save_num, os.path.join(pre_save_name, save_name), save_ext, ENCODING, FILE_ENCODING_VERSION)


def recompile_save_file(save_name:str, new_save_name:str, pre_save_name=SAVES_FOLDER_PATH, new_pre_save_name=SAVES_FOLDER_PATH, save_ext=SAVE_EXT, new_save_ext=SAVE_EXT, save_num=SAVE_SEED, new_save_num=SAVE_SEED):
    """
    Recompiles a save file to a different name/number.
    """
    if new_save_name is None:
        new_save_name = save_name
    try:
        save_data = sfm.decode_save(save_num, os.path.join(pre_save_name, save_name), save_ext, ENCODING)
    except FileNotFoundError:
        print(f"recompile_save_file: FILE {save_name} NOT FOUND!")
        return False
    else:
        sfm.encode_save(save_data, new_save_num, os.path.join(new_pre_save_name, new_save_name), new_save_ext, ENCODING, FILE_ENCODING_VERSION)
        return True




def old_file_reader(save_name:str="save*", save_ext:str=OLD_BACKUP_EXT, dir_name:str=BACKUPS_FOLDER_PATH, decode_until:int=1):
    """
    sfm.file_reader but for backups
    """
    from os import path, listdir

    # get existing file numbers
    file_names = listdir(dir_name)
    existing_files = []
    for name in file_names:
        if path.isfile(path.join(dir_name, name)) and name.find(save_ext) and name.find(save_name.replace("*", "")):
            try: file_number = int(name.replace(f".{save_ext}", "").split(save_name.replace("*", ""))[1])
            except ValueError: continue
            except IndexError: continue
            existing_files.append([name, file_number])
    existing_files.sort()

    file_data = []
    for files in existing_files:
        try:
            try:
                data = sfm.decode_save(files[1], path.join(dir_name, files[0]), "", decode_until=decode_until)
            except ValueError:
                data = -1
        except FileNotFoundError: print("not found " + str(files))
        else:
            file_data.append([files[0].replace("." + OLD_BACKUP_EXT, ""), data])
    return file_data

def get_saves_data():
    """
    main.get_saves_data but for backups
    """

    def process_file(data, old_files=False):
        if data[1] == -1:
            if not old_files:
                errored_new.append(data)
            elif data in errored_new:
                errored_both.append(data)
        else:
            try:
                data[1] = json.loads(data[1][0])
                data_processed = ""
                data_processed += f"\"{data[0]}\"{'(old)' if old_files else ''}: {data[1]['player_name']}\n"
                last_access = data[1]["last_access"]
                data_processed += f"Last opened: {u.make_date(last_access, '.')} {u.make_time(last_access[3:])}"
                # check version
                try: save_version = data[1]["save_version"]
                except KeyError: save_version = 0.0
                data_processed += u.stylized_text(f" v.{save_version}", (Color.GREEN if save_version == SAVE_VERSION else Color.RED))
                if old_files:
                    file_number = int(data[0].replace(f".{OLD_BACKUP_EXT}", "").split("save")[1])
                else:
                    file_number = SAVE_SEED
                datas_processed.append([data[0], data_processed, file_number])
            except (TypeError, IndexError):
                ts.press_key(f"\"{data[0]}\" could not be parsed!")

    ts.recreate_backups_folder()
    ts.recreate_saves_folder()
    # read saves
    datas = sfm.file_reader(-1, None, OLD_BACKUP_EXT, BACKUPS_FOLDER_PATH, save_num=SAVE_SEED)
    datas_old = old_file_reader()
    errored_new = []
    errored_both = []
    # process file data
    datas_processed = []
    for file_data in datas:
        process_file(file_data)
    for file_data in datas_old:
        process_file(file_data, True)
    for wrong in errored_both:
        ts.press_key(f"\"{wrong[0]}\" is corrupted!")
    return datas_processed

def load_backup_menu():
    """
    W.I.P. Backup loading menu.
    """
    files_data = get_saves_data()
    if len(files_data) > 0:
        while True:
            # get data from file_data
            list_data = []
            for data in files_data:
                list_data.append(data[1])
                list_data.append(None)
            option = sfm.UI_list_s(list_data, " Backup loading", True, True, True).display()
            # load
            if option == -1:
                break
            else:
                file_name = str(files_data[int(option)][0])
                save_num = files_data[int(option)][2]
                if recompile_save_file(file_name, file_name, BACKUPS_FOLDER_PATH, SAVES_FOLDER_PATH, OLD_BACKUP_EXT, SAVE_EXT, save_num):
                    input("\n" + file_name + " loaded!")
    else:
        dm.press_key("No backups found!")



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

        try:
            ts.check_package_versions()

            # GLOBAL VARIABLES
            GOOD_PACKAGES = True
            SETTINGS = dm.Settings(ts.settings_manager("auto_save"), ts.settings_manager("keybinds"))
            SETTINGS.save_keybind_mapping()
            SAVE_DATA = dm.Save_data
            GLOBALS = dm.Globals(False, False, False, False)
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
        settings = dm.Settings(ts.settings_manager("auto_save"), ts.settings_manager("keybinds"))
        settings.save_keybind_mapping()
        if settings.auto_save == True or settings.auto_save == False:
            if settings.DOUBLE_KEYS == ts.DOUBLE_KEYS and type(settings.keybinds) is dict:
                print("Passed")
                ts.log_info("Settings checks", "Passed", "PASS")
                good = True
        if not good:
            print("Failed")
            ts.log_info("Settings checks", "Failed", "FAIL")


# Self_Checks()