from colorama import just_fix_windows_console
# just_fix_windows_console()
from colorama import Fore, Back

import os
import psutil
import time
import threading
import random
from datetime import datetime



class DiskDriver:
	def __init__(self):
		print('[START] Initialization of disks driver...')

		self.disks = []
		threading.Thread(target=self.checkingDisks, daemon=True).start()
		print(Fore.YELLOW + '[INFO] Checking system for new devices...')


	def getListOfDisks(self) -> list:
		disksList = []
		partitions = psutil.disk_partitions()
		
		for partition in partitions:
			try: partition_usage = psutil.disk_usage(partition.mountpoint)
			except PermissionError: continue
		
			disksList.append(
				{
					'name': partition.mountpoint,
					'size': partition_usage.total,
					'used': partition_usage.used,
					'usedInPersents': partition_usage.percent
				}
			)

		return disksList


	def checkingDisks(self, delay=1):
		disksCount = len(psutil.disk_partitions())

		while True:
			disksConnectedList = psutil.disk_partitions()

			if disksCount != len(disksConnectedList):
				if len(disksConnectedList) < disksCount: print(Fore.RED + '[DISCONNECT] Disk has been disconnected.')
				elif len(disksConnectedList) > disksCount: print(Fore.GREEN + '[CONNECT] Disk has been connected.')

				self.disks = disksConnectedList
				disksCount = len(disksConnectedList)

			time.sleep(delay)


	def generateFolderName(self, lenth=32):
		letters = [i for i in 'abcdefghijklmnopqrstuvwxyz']
		return ''.join([random.choice(letters) if random.randint(0, 1) else random.choice(letters).upper() for i in range(0, lenth)])

	def getFolderSize(self, path):
		total_size = 0

		for dirpath, dirnames, filenames in os.walk(path):
			for file in filenames:
				fp = os.path.join(dirpath, file)
				total_size += os.path.getsize(fp)

		return total_size


	def getUserPath(self, pathToDisksFolder='/disks/') -> str: # path
		disksLisk = self.getListOfDisks()

		minUsedSpace = None

		for disk in disksLisk:
			if minUsedSpace and disk['name'] not in ['/', 'C:/'] and 'disk' in disk['name']:
				if minUsedSpace['space'] > disk['used']: minUsedSpace = {'name': disk['name'], 'space': disk['used']}
			else:
				if disk['name'] not in ['/', 'C:/'] and 'disk' in disk['name']:
					minUsedSpace = {'name': disk['name'], 'space': disk['used']}

		for obj in os.walk(pathToDisksFolder):
			for diskFolder in obj[1]:
				print(obj[0], diskFolder)
				diskSize = self.getFolderSize(os.path.join(obj[0], diskFolder))

				if minUsedSpace: 
					if diskSize < minUsedSpace['space']:
						minUsedSpace = {'name': os.path.join(obj[0], diskFolder), 'space': diskSize}
				else:
					minUsedSpace = {'name': os.path.join(obj[0], diskFolder), 'space': diskSize}

			break

		if not minUsedSpace:
			print(Fore.RED + '[ERROR] Disk for new users folder has not been found.')

		path = os.path.join(minUsedSpace['name'], self.generateFolderName())
		os.mkdir(path)
		return path


