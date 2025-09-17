#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crawl one or more folder(s) to locate duplicate files.

For efficiency, the proccess has been split into two phases:
	1. Files are grouped by size. (Progress: '.' per file)
	2. Files with matching sizes have their md5 checksum computed. (Progress: 'C' per file) 

'E' in the progressbar denotes an Error. (See stderr for details)

Examples:
	python find_duplicates.py /home/user/Downloads /home/user/Pictures/
	python find_duplicates.py "C:\\Users\\My Name\\Documents" "D:\\Backup\\Documents"
"""

import os
import sys
import hashlib
import argparse

def md5Checksum(filePath):
	with open(filePath, 'rb') as fh:
		m = hashlib.md5()
		while True:
			data = fh.read(8192)
			if not data:
				break
			m.update(data)
		return m.hexdigest()

def main():
	parser = argparse.ArgumentParser(
		description='Find duplicate files based on MD5 checksums.',
		epilog=r'''
Examples:
  %(prog)s /home/user/Downloads /home/user/Pictures/
  %(prog)s "C:\Users\My Name\Documents" "D:\Backup\Documents"
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
	)
	parser.add_argument('folders', nargs='+', help='One or more folders to search for duplicates in.')
	args = parser.parse_args()
	
	sizeTable = dict()
	hashtable = dict()
	filecounter = 0
	filerr = 0

	for root in args.folders: # for each folder given
		for current, dirs, files in os.walk(root): # loop though its contents
			for fname in files: # and for each file you find
				fullname = os.path.join(current, fname)
				filecounter += 1
				print('.', end='', flush=True) # Progressbar 
				try:
					myfilesize = os.path.getsize(os.path.join(current, fname))
				except (PermissionError, FileNotFoundError, OSError) as e:
					print('E', end='', flush=True) # Progressbar
					filerr += 1
					continue
				if myfilesize in sizeTable:
					sizeTable[myfilesize] += (fullname, )
				else:
					sizeTable[myfilesize] = (fullname, )
	for size, filepaths in sizeTable.items():
		if len(filepaths) > 1:
			for fullname in filepaths:
				print('C', end='', flush=True) # Progressbar
				try:
					myfileshash = md5Checksum(fullname)
				except (PermissionError, FileNotFoundError, OSError) as e:
					print('E', end='', flush=True) # Progressbar
					filerr += 1
					continue
				if myfileshash in hashtable:
					hashtable[myfileshash] +=  (fullname, )
				else:
					hashtable[myfileshash] = (fullname, )
	print()
	
	duplicates = 0
	for filehash, paths in hashtable.items():
		if len(paths) > 1:
			print(f"\nDuplicate files found for hash {filehash}:")
			duplicates += 1
			for path in paths:
				print(f"    - {path}")
				
	if duplicates == 0:
		print(f"No duplicate files found among {filecounter} files ({filerr} errors.)")
	else:
		print(f"{duplicates} duplicate files found among {filecounter} files ({filerr} errors.)")
			
if __name__ == '__main__':
	main()
