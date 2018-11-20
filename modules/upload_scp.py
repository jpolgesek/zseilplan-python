#coding: UTF-8
import pysftp 
import modules.utils
import os

class Uploader:
	do_not_upload = [
		"manifest.json",
		"index.html",
		"update.html"
	]

	def __init__(self, hostname):
		self.hostname = hostname
		return
		
	
	def login(self, username, password):
		self.username = username
		self.password = password
		return

	
	def connect(self):
		cnopts = pysftp.CnOpts()
		cnopts.hostkeys = None   
		self.conn = pysftp.Connection(
			host = self.hostname, 
			username = self.username,
			password = self.password,
			cnopts = cnopts
		)
		return

	def chdir(self, directory):
		self.cd = directory
		return self.conn.chdir(directory)
	
	def mkdir(self, directory):
		try:
			with self.conn.cd(self.cd):
				self.conn.mkdir(directory)
		except:
			return False
		return True

	def ls(self):
		return self.conn.listdir()
	
	def fetch_file(self, filename):
		with self.conn.cd(self.cd):
			self.conn.get("temp__{0}__{0}.tmp".format(filename), filename)
			
		with open("temp__{0}__{0}.tmp".format(filename), "r") as f:
			data = f.read()
		
		os.unlink("temp__{0}__{0}.tmp".format(filename))

		return data
	
	def upload_file(self, source, target):
		with self.conn.cd(self.cd):
			return self.conn.put(source, target, preserve_mtime=True)
	
	def upload_dir(self, source, target):
		for root, dirs, files in os.walk(source, topdown=True):
			for name in files:
				with self.conn.cd(target):
					if name in self.do_not_upload: continue
					
					path = os.path.join(root, name).split(source)[1]
					path = path.replace("\\", "/")
					
					dirs_new = path[:path.rfind("/")]

					if len(dirs_new) > 0:
						self.conn.makedirs(target + dirs_new) 
						for d in dirs_new.split("/"):
							self.conn.chdir(d)
					
					try:
						self.conn.put(os.path.join(os.getcwd(), root, name), name, preserve_mtime=True)
						modules.utils.substep("File {} uploaded".format(path))
					except Exception as e:
						modules.utils.substep("File {} was not uploaded".format(path))