import os
import shutil
import zipfile

from tools import SAVES_FOLDER_PATH, BACKUPS_FOLDER_PATH, BACKUP_EXT, ROOT_FOLDER

save_name = "new save"
zip_to = os.path.join(BACKUPS_FOLDER_PATH, save_name)
zip_from = os.path.join(SAVES_FOLDER_PATH, save_name)

# REQUIRES MOVE
def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, BACKUP_EXT, archive_from, archive_to)
    shutil.move('%s.%s'%(name,BACKUP_EXT), destination + "." + BACKUP_EXT)


# COPES FOLDERS UP TO ROOT
def zipppppppp():
    zf = zipfile.ZipFile(zip_to + ".zip", "w")
    for dirname, subdirs, files in os.walk(zip_from):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()


# GOOD
def unzipp(fromm, tooo):
    with zipfile.ZipFile(fromm, 'r') as zip_ref:
        zip_ref.extractall(tooo)


# shutil.make_archive(save_name, BACKUP_EXT, SAVES_FOLDER_PATH, save_name)
# make_archive(zip_from, zip_to)
# unzipp(os.path.join(ROOT_FOLDER, save_name) + ".zip", os.path.join(BACKUPS_FOLDER_PATH, save_name))
zipppppppp()

# 87531