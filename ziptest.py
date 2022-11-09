import os
import shutil
import zipfile

from tools import SAVES_FOLDER_PATH, BACKUPS_FOLDER_PATH, BACKUP_EXT, ROOT_FOLDER, SAVES_FOLDER, BACKUPS_FOLDER, SAVE_FOLDER_NAME_CHUNKS

# REQUIRES MOVE
def make_archive(source:str, destination:str):
    name = os.path.basename(destination).split('.')[0]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, BACKUP_EXT, archive_from, archive_to)
    shutil.move(f"{name}.{BACKUP_EXT}", f"{destination}.{BACKUP_EXT}")


save_name = "new save"
zip_to = os.path.join(BACKUPS_FOLDER_PATH, save_name)
zip_from = os.path.join(SAVES_FOLDER_PATH, save_name)

# COPIES FOLDERS UP TO ROOT
def zipppppppp():
    zf = zipfile.ZipFile(zip_to + f".{BACKUP_EXT}", "w")
    for dirname, subdirs, files in os.walk(os.path.join(SAVES_FOLDER, save_name)):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()


# GOOD
def unzipp(fromm, tooo):
    with zipfile.ZipFile(fromm, 'r') as zip_ref:
        zip_ref.extractall(tooo)


# ALMOST PERFECT!!!
def zipdir(path):
    with zipfile.ZipFile(f"{zip_to}.{BACKUP_EXT}", 'w') as zf:
        for root, dirs, files in os.walk(path):
            for file in files:
                zf.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                                        os.path.join(path, '..')))


# shutil.make_archive(save_name, BACKUP_EXT, SAVES_FOLDER_PATH, save_name)
# make_archive(zip_from, zip_to)
# unzipp(os.path.join(ROOT_FOLDER, save_name) + ".zip", os.path.join(BACKUPS_FOLDER_PATH, save_name))
# zipppppppp()
zipdir(zip_from)

# 87531