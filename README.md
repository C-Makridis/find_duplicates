# find_duplicates
Small python script to locate duplicate files in multiple paths / partitions / disks.

For efficiency, the proccess has been split into two phases:

1. Files are grouped by size. (Progress: '.' per file)
1. Files with matching sizes have their md5 checksum computed. (Progress: 'C' per file) 

    'E' in the progressbar denotes an Error. (See stderr for details)

## Examples:
	python find_duplicates.py /home/user/Downloads /home/user/Pictures/
	python find_duplicates.py "C:\\Users\\My Name\\Documents" "D:\\Backup\\Documents"
	python find_duplicates.py --greater-than 5 /mnt/backup  # Find duplicates larger than 5MB
	python find_duplicates.py -d -l /home/user/find_duplicates.log /opt/

 ## Note:
 1. Depending on the number and size of duplicate files, this can take a loooooot of time!
 1. Having debug enabled can also create a huge log file. 
