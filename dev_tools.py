
from tools import sfm
from tools import SAVES_FOLDER_PATH, SAVE_NAME, SAVE_EXT, SAVE_FILE_PATH
from tools import ENCODING, SETTINGS_ENCODE_SEED, FILE_ENCODING_VERSION

def decode_save_file(save_num=1, save_name=SAVE_FILE_PATH):
    """
    Decodes a save file into a normal json.
    """
    try:
        save_data = sfm.decode_save(save_num, save_name, SAVE_EXT, ENCODING)
    except FileNotFoundError:
        print("decode_save_file: FILE NOT FOUND!")
    else:
        f = open(f'{save_name.replace("*", str(save_num))}.decoded.json', "w")
        for line in save_data:
            f.write(line + "\n")
        f.close()


def encode_save_file(save_num=1, save_name=SAVE_FILE_PATH):
    """
    Encodes a json file into a .sav file.
    """
    try:
        f = open(f'{save_name.replace("*", str(save_num))}.decoded.json', "r")
        save_data = f.readlines()
        f.close()
        save_data_new = []
        for line in save_data:
            save_data_new.append(line.replace("\n", ""))
    except FileNotFoundError:
        print("encode_save_file: FILE NOT FOUND!")
    else:
        sfm.encode_save(save_data_new, save_num, save_name, SAVE_EXT, ENCODING, FILE_ENCODING_VERSION)


def recompile_save_file(save_num=1, new_save_num=1, save_name=SAVE_FILE_PATH, new_save_name=SAVE_FILE_PATH, save_ext=SAVE_EXT, new_save_ext=SAVE_EXT):
    """
    Recompiles a save file to a different name/number.
    """
    try:
        save_data = sfm.decode_save(save_num, save_name, save_ext, ENCODING)
    except FileNotFoundError:
        print("recompile_save_file: FILE NOT FOUND!")
    else:
        sfm.encode_save(save_data, new_save_num, new_save_name, new_save_ext, ENCODING, FILE_ENCODING_VERSION)

# thread_1 = threading.Thread(target="function", name="Thread name", args=["argument list"])
# thread_1.start()
# merge main and started thread 1?
# thread_1.join()
