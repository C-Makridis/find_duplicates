#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crawl one or more folders to locate duplicate files.

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
import logging

logger = logging.getLogger(__name__)

def arguments_Parser():
	parser = argparse.ArgumentParser(
		prog = 'find_duplicates',
		description='Find duplicate files based on MD5 checksums.',
		epilog=r'''
	Examples:
	%(prog)s /home/user/Downloads /home/user/Pictures/
	%(prog)s "C:\Users\My Name\Documents" "D:\Backup\Documents"
	%(prog)s --greater-than 5 /mnt/backup  # Find duplicates larger than 5MB
		''',
		formatter_class=argparse.RawDescriptionHelpFormatter
	)
	parser.add_argument('-gt', '--greater-than', type=float, metavar='SIZE_MB', help='Only consider files larger than SIZE_MB megabytes.')
	parser.add_argument('-d', '--debug', action='store_true', help='Enable verbose debug logging. Note this can create HUGE files.')
	parser.add_argument('-l', '--log-file', help='Custom log file path. Defaults to current directory.')
	parser.add_argument('folders', nargs='+', help='One or more folders to search for duplicates in.')
	return parser.parse_args()

def build_size_table(args):
	sizeTable = dict()
	filecounter = 0
	filerr = 0
	size_threshold_bytes = args.greater_than * 1024 * 1024 if args.greater_than else 0
	
	for root in args.folders: # for each folder given
		for current, dirs, files in os.walk(root): # loop though its contents
			for fname in files: # and for each file you find
				fullname = os.path.join(current, fname)
				filecounter += 1
				try:
					myfilesize = os.path.getsize(fullname)
					print('.', end='', flush=True) # Progressbar
					logger.debug(f"Size of {fullname} is {myfilesize}")
				except (PermissionError, FileNotFoundError, OSError) as e:
					print('E', end='', flush=True) # Progressbar
					logger.error(f"Failed to check file {fullname}")
					logger.error(str(e))
					filerr += 1
					continue
				if myfilesize > size_threshold_bytes:
					if myfilesize in sizeTable:
						sizeTable[myfilesize] += (fullname, )
					else:
						sizeTable[myfilesize] = (fullname, )
	return filecounter, sizeTable, filerr

def hash_suspected_files(sizeTable, filerr):
	hashtable = dict()
	for size, filepaths in sizeTable.items():
		if len(filepaths) > 1:
			for fullname in filepaths:
				try:
					myfileshash = md5Checksum(fullname)
					print('C', end='', flush=True) # Progressbar
					logger.debug(f"Hash of {fullname} is {myfileshash}")
				except (PermissionError, FileNotFoundError, OSError) as e:
					print('E', end='', flush=True) # Progressbar
					logger.error(f"Failed to check file {fullname}")
					logger.error(str(e))
					filerr += 1
					continue
				if myfileshash in hashtable:
					hashtable[myfileshash] +=  (fullname, )
				else:
					hashtable[myfileshash] = (fullname, )
	return hashtable, filerr

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
	
	args = arguments_Parser()
	
	log_level = logging.DEBUG if args.debug else logging.INFO
	log_file = getattr(args, 'log_file', 'find_duplicates.log')
	
	logging.basicConfig(filename=log_file, format='%(asctime)s %(levelname)s|%(message)s', datefmt=("%Y-%m-%d %H:%M:%S"), level=log_level)# stream=sys.stdout for console
	logger.info(f"Starting duplicate search with arguments: {vars(args)}")
	logger.info("Group files by size.");
	filecounter, sizeTable, filerr = build_size_table(args)
	logger.debug(f"{filecounter} files found with {filerr} errors.")
	logger.info("Hash files with matching sizes.");
	hashtable, filerr = hash_suspected_files(sizeTable, filerr) 
	logger.debug(f"{filerr} errors while hashing .")
	
	print()
	
	duplicates = 0
	for filehash, paths in hashtable.items():
		if len(paths) > 1:
			print(f"\nDuplicate files found for hash {filehash}:")
			for path in paths:
				duplicates += 1
				print(f"    - {path}")
	
	print('-'*60)
	
	print(f"{'No' if duplicates == 0 else duplicates } duplicate files {f'above {args.greater_than} MB' if args.greater_than else '' } found among {filecounter} files ({filerr} errors.) under path(s):")


	for path in args.folders:
		print(f' * {path}')
	
	logger.info("Run completed.");
	
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		try:
			logger.error("User interrupted execution")
			sys.exit(1)
		except NameError:
			logging.error("User interrupted execution before logger initialization")
			print("\nInterrupted by user.")
			sys.exit(1)
	except Exception as e:
		logging.critical(f"Unexpected error: {e}")
		sys.exit(1)
