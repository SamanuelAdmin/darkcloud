from colorama import just_fix_windows_console
# just_fix_windows_console()
from colorama import init
init(autoreset=True)
from colorama import Fore, Style

import shutil
import hashlib


class User:
	def __init__(self, usersDatabase, userName, userFreeSpace=2*1024*1024*1024):
		self.userFreeSpace = userFreeSpace
		self.userName = userName
		self.ifVerifed = False

		self.usersDatabase = usersDatabase


	def check(self, password, generatePathFunc):
		hashObj = hashlib.md5()
		hashObj.update(password.encode())
		password = hashObj.hexdigest()

		if self.userName in self.usersDatabase.d:
			if password == self.usersDatabase.d[self.userName]['password']:
				print(f'[INFO] User "{self.userName}" has been logined.')
				return 1

			return 0
		else:
			path = generatePathFunc()
			self.usersDatabase.d[self.userName] = {'password': password, 'fc': self.userFreeSpace, 'path': path}
			self.usersDatabase.save()
			print(Fore.GREEN + f'[SET] User "{self.userName}" has been added to database with path "{path}".')
			return 1

