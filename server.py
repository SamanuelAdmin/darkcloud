# from colorama import just_fix_windows_console
# just_fix_windows_console()
from colorama import init
init(autoreset=True)
from colorama import Fore, Style

from flask import Flask, request, send_from_directory, render_template, session
from flask_session import Session
from redis import Redis
from flask_session.__init__ import Session
from markupsafe import Markup
import os
import random
import time
import copy



class WebServer:
	def __init__(self, userClass, getUserPathFunc, configs, usersDatabase, templatesFolderName=os.path.join(os.getcwd(), 'templates')):
		self.userClass = userClass
		self.getUserPathFunc = getUserPathFunc
		self.configs = configs
		self.templatesFolderName = templatesFolderName
		self.usersDatabase = usersDatabase
		self.captchaList = configs['captcha']
		self.pathToStaticFolder = os.path.join(os.getcwd(), 'static')

		self.checkLoginLink = ''.join([random.choice([i for i in 'abcdefghijklmnopqrstuvwxyz']) if random.randint(0, 1) else random.choice([i for i in 'abcdefghijklmnopqrstuvwxyz']).upper() for i in range(0, 16)])

		self.mainApp = None



	def generateUserID(self, lenth=32): return ''.join([str(random.randint(0, 9)) for i in range(0, lenth)])


	def redirectPage(self, link, text=None, script=''):
		if not text: text = f'<h1>JavaScript is turned off in your browser, so you need to do it by yourself. <br> <a href="{link}">CLICK HERE</a></h1>'

		return f'<!DOCTYPE html><html><head></head><body><script>{script}location.href="{link}"</script>{text}</body></html>'


	def getUsedScapeSize(self, path):
		total_size = 0

		for dirpath, dirnames, filenames in os.walk(path):
			for file in filenames:
				file_path = os.path.join(dirpath, file)
				total_size += os.path.getsize(file_path)

		return total_size


	def getFileListItem(self, path, filename):
		return f'''
<tr>
	<th scope="row"><a href="/delete/{filename}">DEL</a></th>
	<th scope="row"><a href="/getlink/{filename}">get link</a></th>
	<td><a href="/download/{filename}">{filename}</a></td>
	<td>{round(os.path.getsize(os.path.join(path, filename)) / 1024 / 1024, 3)} MB</td>
	<td>{time.ctime(os.stat(os.path.join(path, filename)).st_ctime)}</td>
</tr>'''


	def generateCaptcha(self):
		word = random.choice(list(self.captchaList.keys()))
		session['captchaCorrectWord'] = word

		return self.captchaList[word]

	def generateFileKey(self, lenth=48):
		letters = [i for i in 'abcdefghijklmnopqrstuvwxyz0123456789']
		return ''.join([random.choice(letters) if random.randint(0, 1) else random.choice(letters).upper() for i in range(0, lenth)])


	def init(self):
		print('[START] Initialization of web server.')

		self.mainApp = Flask(__name__, template_folder=self.templatesFolderName)
		self.mainApp.secret_key = ''.join([str(random.randint(0, 9)) for i in range(0, 32)])

		self.mainApp.config['SESSION_TYPE'] = 'redis'
		self.mainApp.config['SESSION_REDIS'] = Redis(host='192.168.0.107', port=6379)
		
		Session(self.mainApp)


		@self.mainApp.route('/')
		def index():
			try:
				session['id']
				session['active']
			except:
				session['id'] = self.generateUserID()
				session['active'] = False

			if not session['active']: return self.redirectPage('/login')
			

			usedSpaceSize = self.getUsedScapeSize(self.usersDatabase.getValue(session['name'])['path'])

			listOfFiles = ''
			for dirpath, dirnames, filenames in os.walk(self.usersDatabase.getValue(session['name'])['path']):
				for file in filenames:
					listOfFiles += self.getFileListItem(dirpath, file)

			try: 
				if session['message']:
					message = copy.copy(session['message'])
					del session['message']

					return message
			except: pass

			return render_template('index.html', listOfFiles=Markup(listOfFiles), userName=session['name'], usingSpace=round(usedSpaceSize / 1024 / 1024 / 1024, 3), totalSpace=str(round(self.usersDatabase.getValue(session['name'])['fc'] / 1024 / 1024 / 1024, 3)))


		@self.mainApp.route('/login')
		def login():
			try:
				session['id']
				session['active']
			except:
				session['id'] = self.generateUserID()
				session['active'] = False

			captchaPath = self.generateCaptcha()
			return render_template('login.html', checkLoginLink=self.checkLoginLink, script='$Admin', captchaPath=captchaPath)


		@self.mainApp.route('/logout')
		def logout():
			try:
				session['id']
				session['active']
				session['name']
			except: return self.redirectPage('/')

			try: print(f'[INFO] {session["name"]} has logout.')
			except: pass

			del session['id']
			del session['active'] 
			del session['name']

			return self.redirectPage('/')


		@self.mainApp.route('/' + self.checkLoginLink, methods=['POST'])
		def checklogin():
			try:
				session['id']
				session['active']
			except:
				session['id'] = self.generateUserID()
				session['active'] = False

			if session['active']: return self.redirectPage('/')


			captchaWord = request.form.get('captcha').replace('<', '').replace('>', '')

			if captchaWord != session['captchaCorrectWord']:
				captchaPath = self.generateCaptcha()
				return render_template('login.html', checkLoginLink=self.checkLoginLink, script="Incorrect captcha!", captchaPath=captchaPath)


			login = request.form.get('login').replace('<', '').replace('>', '')
			password = request.form.get('password')

			if login and password:
				newUser = self.userClass(self.usersDatabase, login, userFreeSpace=self.configs['user']['baseFreeSpaceForUser'])
				checkingResult = newUser.check(password, self.getUserPathFunc)

				if checkingResult:
					session['active'] = True
					session['name'] = newUser.userName
					return self.redirectPage('/')

				captchaPath = self.generateCaptcha()
				return render_template('login.html', checkLoginLink=self.checkLoginLink, script="Wrong password!", captchaPath=captchaPath)

			captchaPath = self.generateCaptcha()
			return render_template('login.html', checkLoginLink=self.checkLoginLink, script=Markup('Error: arguments has not been found.'), captchaPath=captchaPath)


		@self.mainApp.route('/download/<path:filename>')
		def downloadFile(filename):
			try:
				session['id']
				session['active']
			except:
				session['id'] = self.generateUserID()
				session['active'] = False

			if not session['active']: return self.redirectPage('/login')


			filePath = os.path.join(self.usersDatabase.getValue(session['name'])['path'], filename)

			try: open(filePath)
			except: return f'File "{filePath}" has not been found.'

			print(Fore.GREEN + f'[INFO] File "{filename}" has been downloaded by "{session["name"]}".')

			return send_from_directory(directory=self.usersDatabase.getValue(session['name'])['path'], path=filename, as_attachment=True)


		@self.mainApp.route('/delete/<path:filename>')
		def deleteFile(filename):
			try:
				session['id']
				session['active']
			except:
				session['id'] = self.generateUserID()
				session['active'] = False

			if not session['active']: return self.redirectPage('/login')


			filePath = os.path.join(self.usersDatabase.getValue(session['name'])['path'], filename)

			try: open(filePath)
			except: return f'File "{filePath}" has not been found.'

			os.remove(filePath)
			try: os.remove(filePath + '.key')
			except: pass

			print(Fore.GREEN + f'[INFO] File "{filename}" has been deleted by "{session["name"]}".')

			return self.redirectPage('/')
			

		@self.mainApp.route('/getlink/<path:filename>')
		def getFileLink(filename): 
			try:
				session['id']
				session['active']
			except:
				session['id'] = self.generateUserID()
				session['active'] = False

			if not session['active']: return self.redirectPage('/login')

			filePath = os.path.join(self.usersDatabase.getValue(session['name'])['path'], filename)

			try: open(filePath)
			except: return f'File "{filePath}" has not been found.'

			fileKey = self.generateFileKey()
			fileKeyPath = os.path.join(self.usersDatabase.getValue(session['name'])['path'], f'{filename}.key')
			open(fileKeyPath, 'w').write(fileKey)

			fileLink = f'/getfilebylink/{session["name"]}/{filename}/{fileKey}'

			print(f'[NEW] Link to file "{filename}" has been created by {session["name"]}.')
			print(fileLink)

			return self.redirectPage('/', text=f'<h1>Your link is: [this domen]{fileLink} .<br>And please, turn off NoScript :3</h1>', script=f'alert("Your link is: \n" + window.location.hostname + "{fileLink}");')


		@self.mainApp.route('/getfilebylink/<path:accountname>/<path:filename>/<path:filekey>')
		def getFileByLink(accountname, filename, filekey):
			try:
				session['id']
				session['active']
			except:
				session['id'] = self.generateUserID()
				session['active'] = False

			try:
				pathToKeyFile = os.path.join(self.usersDatabase.getValue(accountname)['path'], filename + '.key')
				open(os.path.join(self.usersDatabase.getValue(accountname)['path'], filename))

				if open(pathToKeyFile).read() != filekey: raise Exception()
			except: return '<h1>Link to file is incorrect!</h1>'

			return send_from_directory(
					directory=self.usersDatabase.getValue(accountname)['path'], 
					path=filename, 
					as_attachment=True
				)


		@self.mainApp.route('/upload', methods=['POST'])
		def uploadFile():
			try:
				session['id']
				session['active']
			except:
				session['id'] = self.generateUserID()
				session['active'] = False

			if not session['active']: return self.redirectPage('/login')


			if 'file' in request.files:
				gottenFile = request.files['file']
				fileSize = request.content_length
				fileName = gottenFile.filename

				for blockedSymvol in ['#', '/', '@', '\\', '|', "'", '"', ' ']:
					if blockedSymvol in fileName: fileName.replace(blockedSymvol, '')

				freeSpaceSize = self.usersDatabase.getValue(session['name'])['fc'] - self.getUsedScapeSize(self.usersDatabase.getValue(session['name'])['path'])

				if fileSize < freeSpaceSize:
					filePath = os.path.join(self.usersDatabase.getValue(session['name'])['path'], fileName)

					try: gottenFile.save(filePath)
					except:
						session['message'] = '<h1>Disk with your folder has been disconnected from a cloud. Please, tell to developers or maintenance workers about your problem.</h1>'

					freeSpaceSize = self.usersDatabase.getValue(session['name'])['fc'] - self.getUsedScapeSize(self.usersDatabase.getValue(session['name'])['path'])

					print(Fore.GREEN + f'[GET] File "{fileName}" has been gotten and saved to "{filePath} (Free space: {round(freeSpaceSize / 1024 / 1024)}MB)".')

				else: session['message'] = f'<h1>You have not enough space on your cloud part! You have only {round(freeSpaceSize / 1024 / 1024)}MB.</h1>'

			return self.redirectPage('/')



	def start(self):
		print('[START] Starting web server...')
		self.mainApp.run(
				host=self.configs['server']['ip'] if self.configs['server']['ip'] != 'none' else open('/home/admin_/ip').read() if open('/home/admin_/ip').read()[-1] != '\n' else open('/home/admin_/ip').read()[:-1],
				port=int(self.configs['server']['port'] if self.configs['server']['port'] != 'none' else open('/home/admin_/port').read() if open('/home/admin_/port').read()[-1] != '\n' else open('/home/admin_/port').read()[:-1])
			)
