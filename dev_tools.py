
from tools import sfm, r
from tools import MAIN_THREAD_NAME, AUTO_SAVE_THREAD_NAME, MANUAL_SAVE_THREAD_NAME, SAVES_FOLDER_PATH, SAVE_NAME, SAVE_EXT, SAVE_FILE_PATH, AUTO_SAVE_DELAY, ENCODING, SETTINGS_ENCODE_SEED

def decode_save_file(save_num=1, save_name=SAVE_FILE_PATH):
    """
    Decodes a save file into a normal txt.
    """
    try:
        save_data = sfm.decode_save(save_num, save_name, SAVE_EXT, ENCODING)
    except FileNotFoundError:
        print("decode_save_file: FILE NOT FOUND!")
    else:
        f = open(f'{save_name.replace("*", str(save_num))}.decoded.txt', "w")
        for line in save_data:
            f.write(line + "\n")
        f.close()


def encode_save_file(save_num=1, save_name=SAVE_FILE_PATH):
    """
    Encodes a txt file into a .sav file.
    """
    try:
        f = open(f'{save_name.replace("*", str(save_num))}.decoded.txt', "r")
        save_data = f.readlines()
        f.close()
        save_data_new = []
        for line in save_data:
            save_data_new.append(line.replace("\n", ""))
    except FileNotFoundError:
        print("decode_save_file: FILE NOT FOUND!")
    else:
        sfm.encode_save(save_data_new, save_num, save_name, SAVE_EXT, ENCODING, 2)


# thread_1 = threading.Thread(target="function", name="Thread name", args=["argument list"])
# thread_1.start()
# merge main and started thread 1?
# thread_1.join()
