# find_duplicates
Small python script to locate duplicate files in multiple paths / partitions / disks.

For efficiency, the proccess has been split into two phases:

1. Files are grouped by size. (Progress: '.' per file)
1. Files with matching sizes have their md5 checksum computed. (Progress: 'C' per file) 

    'E' in the progressbar denotes an Error. (See stderr for details)

## Examples:
	python find_duplicates.py /home/user/Downloads /home/user/Pictures/
	python find_duplicates.py "C:\\Users\\My Name\\Documents" "D:\\Backup\\Documents"
