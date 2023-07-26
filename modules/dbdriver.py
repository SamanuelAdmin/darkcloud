import shelve


class Database:
	def __init__(self, path):
		self.path = path
		self.d = shelve.open(path)

	def save(self):
		self.d.close()
		self.d = shelve.open(self.path)

	def getValue(self, key):
		self.d.close()
		self.d = shelve.open(self.path)
		return self.d[key]
		


class DatabaseDriver:
	def __init__(self):
		self.databases = {}

	def loadDatabase(self, name, path):
		self.databases[name] = Database(path)