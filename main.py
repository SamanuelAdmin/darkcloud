from colorama import just_fix_windows_console
just_fix_windows_console()
from colorama import init
init(autoreset=True)
from colorama import Fore, Style

from modules import diskdriver
from modules import configsreader
from modules import user
from modules import dbdriver
import server


CONFIGS_FOLDER_NAME = 'configs'


def close():
	print(Fore.YELLOW + '[EXIT] Closing...')
	print(Style.RESET_ALL)

def loadDatabases(mainConfigs):
	databaseDriver = dbdriver.DatabaseDriver()
	for name in mainConfigs['database']: databaseDriver.loadDatabase(name, mainConfigs['database'][name])
	return databaseDriver


def main():
	configsModule = configsreader.Configs(CONFIGS_FOLDER_NAME)
	configsModule.initConfigs()
	mainConfigs = configsModule.configs

	diskDriver = diskdriver.DiskDriver()
	databaseDriver = loadDatabases(mainConfigs)
	webServer = server.WebServer(
			user.User, 
			diskDriver.getUserPath, 
			mainConfigs, 
			databaseDriver.databases['usersDatabase'],
		)

	webServer.init()
	webServer.start()

if __name__ == '__main__':
	try: main()
	except KeyboardInterrupt: close()