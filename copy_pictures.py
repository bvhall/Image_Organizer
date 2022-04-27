# copy_pictures.py - Written by Ben Hall
# A simple script that automates the management of pictures.

import sys
from pathlib import Path
import exifread
import shutil
import hashlib


FILENAME = "copy_pictures.py"

HASH_FILENAME = "Hashfile.txt"
HASH_LINE_LEN = 32

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
    ]

EXIFREAD_ALLOWED_EXTS = ["*.jpg", "*.jpeg", "*.heic"]

# Copies the image according to predefined rules
# Todo: add PNG support
# Todo: add video support

def copy_image(date_str, image_file, image_path):
    # sanity check
    assert image_file.closed == False

    # if date is unknown, copy to unknown folder
    if date_str == "-1":
        # create unknown folder (if it doesn't already exist)
        unknown_path = dest.joinpath("Unknown")
        unknown_path.mkdir(exist_ok=True)

        print("Unknown file detected.")

        # copy file
        shutil.copy2(str(image_path), str(unknown_path))

    # else, first create year, then month, then day folders and copy image.
    else:
        # convert date_str to something usable by datetime
        # Note: I shouldn't really hard code these slices, but it will have to do
        year = date_str[0:4]
        month_num = int(date_str[5:7])
        day = date_str[8:10]

        print("year = " + year + " month = " + str(month_num) + " day = " + day) # debug

        # create / navigate directories
        # print(month_num)

        # create year path and folder (if it doesn't already exist)
        year_path = dest.joinpath(year)
        year_path.mkdir(exist_ok=True)

        # create month path and folder (if it doesn't already exist)
        month_path = year_path.joinpath(MONTHS[month_num - 1])
        month_path.mkdir(exist_ok=True)

        # create day path and folder (if it doesn't already exist)
        day_path = month_path.joinpath(day)
        day_path.mkdir(exist_ok=True)

        # copy file
        # todo: logic for when identical filenames are copied.
        shutil.copy2(str(image_path), str(day_path))


    # close image file
    image_file.close()

# hashes file, checks if it exists then places into hash set and hash file
def process_hash (raw_path) -> bool:
    
    unique = False  # Initially, assume that image is not unique
    path_str = str(raw_path)
    # Todo: create a more optimized solution for saving / checking hashes
    image = open(path_str, "rb")
    image_bytes = image.read(-1)
    image_hash = hashlib.sha256()
    image_hash.update(image_bytes)
    digest = int(image_hash.hexdigest(), base=16)

    # if image is detected, write it to hashset. Then flip unique var
    if digest not in hash_set:
        hash_set.add(digest)
        unique = True
    
    image.close()
    return unique


def exifread_process(image):
     # open image
     image_file = open(image, 'rb')

    # check for duplicates, continue if already exists
     if process_hash(image):

         # extract EXIF metadata
         exif_tags = exifread.process_file(image_file, details=False)

         # extract date and time if it exists
         image_date_tag = str()

         if "EXIF DateTimeOriginal" in exif_tags.keys():
             image_date_tag = exif_tags["EXIF DateTimeOriginal"].printable
             # print(image_date_tag)

         else:
            image_date_tag = "-1"

         copy_image(image_date_tag, image_file, image)


def video_process(image):
    print("stub")

def png_process(image):
    print("stub")


# A simple recursive DFS implmentation for scanning images

# Note: Switched from BFS as with excluding symlinks,
# DFS is equivalent in function with lower cost.
def scan_directory(directory):
    try: 
        
        # add subdirectories to stack
        # get path object for the directory to scan
        # ~~how can I get away with this?~~
        target_dir = Path(directory)
        assert target_dir.is_dir()
        
        # create directory iterator
        scan_iterator = target_dir.iterdir()

        # get subdirectories, discarding symlinks to prevent infinite loops.
        for i in target_dir.iterdir():
            if i.is_dir() and not i.is_symlink():
                #print("scandir l1:" + str(i))
                scan_directory(i)

        # get images to copy
        images = list()
        for i in target_dir.iterdir():
            for x in EXIFREAD_ALLOWED_EXTS:
                if i.match(x):
                    images.append(i)
                    # process_hash(i)
                    
        # call copy_images whenever image file is encountered.
        for i in images:
            exifread_process(i)
    
    # Catch-all exception handling is used as specific behaviour for recovering from an exception is not required
    except BaseException as err:
        print(err)

# MAIN
# For future testing / usage, this code should be able to run as module. For now, this is prevented
if __name__ != "__main__":
    print(f"{FILENAME}: This code is not intended to be executed as a module. Abort.")

# Sanity check parameters
# check for two arguments: target and destination
accepted_num_params = 3

if len(sys.argv) != accepted_num_params:
    print(f"{FILENAME}: expected target and destination")
    sys.exit("-1")

# get path of target and dest
target = Path(sys.argv[1])
dest = Path(sys.argv[2])

# create / load hash file
hash_file_path = dest.joinpath(HASH_FILENAME)
hash_file_path.touch(exist_ok=True)

hash_file = open(hash_file_path, "r")
hash_set = set()
line_begin = 0
line_end = 0

# convert hashfile to set
current_digest = hash_file.readline()

while current_digest != "":
    
    try:
        hash_set.add(int(current_digest, base=16))
    
    except ValueError:
        print("'" + str(current_digest) + "'" + " could not be read as a hex int!")
    
    current_digest = hash_file.readline()

hash_file.close()

# check if directories are valid
directory_invalid = False
if target.is_dir() != True:
    print(f"{FILENAME}: Target directory invalid!")
    directory_invalid = True

# note to self: implement dest directory creation upon being given a non-existent path
if dest.is_dir() != True:
    print(f"{FILENAME}: Destination directory invalid!")
    directory_invalid = True

if directory_invalid:
    sys.exit("-2")

# Execute copy operation

scan_directory(target)

# dump set into hashfile
hash_file = open(hash_file_path, "w")
for x in hash_set:
    hash_file.write(hex(x) + "\n")


hash_file.close()