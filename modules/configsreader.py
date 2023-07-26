from colorama import just_fix_windows_console
# just_fix_windows_console()
from colorama import init
init(autoreset=True)
from colorama import Fore, Style

import os
import json


class Configs:
	def __init__(self, configsFolderName):
		print('[START] Initialization of configs module...')

		self.configsFolderName = configsFolderName
		self.configs = {}


	def initConfigs(self):
		print(f'[GET] Getting configs from {self.configsFolderName}.')

		configs = {}
		configFilesCount = 0
		errorConfigsFilesCount = 0

		for obj in os.walk(self.configsFolderName):
			for fileName in obj[2]:
				if '.json' in fileName:
					filePath = os.path.join(obj[0], fileName)

					try:
						configs[fileName.replace('.json', '')] = json.loads(open(filePath).read())
						print(Fore.GREEN + f'[GET] Gotten configs from "{filePath}".')
						configFilesCount += 1

					except Exception as error:
						print(error)
						print(Fore.RED + f'[ERROR] Cannot read file {filePath}.')
						errorConfigsFilesCount += 1

		print(Fore.YELLOW + f'[INFO] Successfully read files: {configFilesCount}.')
		print(Fore.YELLOW + f'[INFO] Cannot read {errorConfigsFilesCount} files.')

		self.configs = configs