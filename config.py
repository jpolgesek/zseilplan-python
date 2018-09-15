#coding: utf-8
import utils

debug_type = 1

class ConfigFile:
	def __init__(self):
		self.timetable_url = "http://www.zseil.edu.pl/rnowa/html/"
		self.timetable_engine = "vulcan"

		self.overrides_url = ""
		self.overrides_engine = "www"

		self.vulcan_login = "TODO"
		self.vulcan_password = "TODO"

		self.overrides_stats = True
		self.overrides_archiver = True
		self.timetable_archiver = True
		
		#self.ftp_upload = False
		#self.ftp_host = "127.0.0.1"
		#self.ftp_dir = "/polgesek.pl/dev/zseilplan/new_test"
		#self.ftp_user = "user"
		#self.ftp_password = "pass"
		

	def load_target(self, url):
		if url not in targets:
			return False

		self.target = targets[url]
		return True
	
	def print(self):
		print("[*] Załadowana konfiguracja:")
		print("[*] - Silnik planu lekcji: {}".format(self.timetable_engine))

		if self.timetable_engine == "www":
			print("[*] - URL planu lekcji: {}".format(self.timetable_url))
		elif self.timetable_engine == "vulcan":
			print("[*] - Vulcan login: {}".format(self.vulcan_login))

		print("[*] - Silnik listy zastępstw: {}".format(self.overrides_engine))

		if self.overrides_engine == "www":
			print("[*] - URL listy zastępstw: {}".format(self.overrides_url))
		elif self.overrides_engine == "vulcan":
			print("[*] - Vulcan login: {}".format(self.vulcan_login))

		if self.overrides_stats:
			print("[*] - Statystyki zastępstw: Włączone")
		else:
			print("[*] - Statystyki zastępstw: Wyłączone")

		if self.overrides_archiver:
			print("[*] - Archiwizacja zastępstw: Włączone")
		else:
			print("[*] - Archiwizacja zastępstw: Wyłączone")

		if self.timetable_archiver:
			print("[*] - Archiwizacja planu: Włączone")
		else:
			print("[*] - Archiwizacja planu: Wyłączone")

		if self.target['ftp_enable']:
			print("[*] - FTP Upload: Włączone")
		else:
			print("[*] - FTP Upload: Wyłączone")

		print("[*] Rozpoczynam działanie\n")
		return True

'''
PROD: 
user: ***REMOVED***
pass: ***REMOVED***
host: polgesek.pl
'''

targets = {}

targets["testplan.polgesek.pl"] = {
	"dev": True,
	"http_rootdir": "/",
	"hostname": "testplan.polgesek.pl",
	"ftp_user": "***REMOVED***",
	"ftp_pass": "***REMOVED***",
	"ftp_rootdir_manifest": "/",
	"ftp_rootdir_app": "/",
	"ftp_enable": True
}

targets["dev.polgesek.pl"] = {
	"dev": False,
	"http_rootdir": "/",
	"hostname": "dev.polgesek.pl",
	"ftp_user": "***REMOVED***",
	"ftp_pass": "***REMOVED***",
	"ftp_rootdir_manifest": "/",
	"ftp_rootdir_app": "/zseilplan",
	"ftp_enable": True
}

targets["plan.zseil.pl"] = {
	"dev": False,
	"http_rootdir": "/",
	"hostname": "plan.zseil.pl",
	"ftp_user": "",
	"ftp_pass": "",
	"ftp_rootdir_manifest": "/",
	"ftp_rootdir_app": "/",
	"ftp_enable": True
}