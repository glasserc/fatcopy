import shutil
import os.path

listdir = os.listdir
copyfile = shutil.copy2  # copy followed by copystat
mkdir = os.mkdir
exists = os.path.exists
isdir = os.path.isdir
