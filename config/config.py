#coding: utf-8
import os
import modules.utils
from config.targets import targets

debug_type = 1

class Config:
	def __init__(self):
		self.debug_type = 1
		self.timetable_url = "http://www.zseil.edu.pl/rnowa/html/"
		self.timetable_engine = "www"

		self.overrides_url = "http://www.zseil.edu.pl/zastepstwa/"
		self.overrides_engine = "www"

		self.vulcan_login = None
		self.vulcan_password = None
		self.vulcan_access = None

		try:
			with open(os.path.join("config", "secrets.txt"), "r") as f:
				import base64
				self.vulcan_login, self.vulcan_password = base64.b64decode(f.read().encode("UTF-8")).decode("UTF-8").split(":")
				self.vulcan_access = "teacher"
		except:
			pass

		self.overrides_stats = True
		self.overrides_archiver = True
		self.timetable_archiver = True

		self.teacher_recovery_filename = os.path.join("preparsed", "teacher_recovery.json")
		self.teachermap_filename = os.path.join("preparsed", "teachermap.json")
		self.timesteps_filename = os.path.join("preparsed", "timesteps.json")

		self.output_data_path = os.path.join("output", "data.json")
		
		#self.ftp_upload = False
		#self.ftp_host = "127.0.0.1"
		#self.ftp_dir = "/polgesek.pl/dev/zseilplan/new_test"
		#self.ftp_user = "user"
		#self.ftp_password = "pass"
		

	def load_target(self, url):
		if url not in targets:
			return False

		self.target = targets[url]
		if self.target["uploader"] == "ftp":
			import modules.upload_ftp
			self.uploader = modules.upload_ftp.Uploader(self.target["hostname"])
			self.uploader.login(
				self.target["ftp"]["user"], 
				self.target["ftp"]["pass"]
				)
		elif self.target["uploader"] == "scp":
			import modules.upload_scp
			self.uploader = modules.upload_scp.Uploader(self.target["hostname"])
			self.uploader.login(
				self.target["scp"]["user"], 
				self.target["scp"]["pass"]
				)
		elif self.target["uploader"] == "local":
			import modules.upload_local
			self.uploader = modules.upload_local.Uploader(self.target["hostname"])
		else:
			print("Moduł uploadu {} nie istnieje".format(self.target["uploader"]))
			exit(1)
	
		self.target["rootdir_app"] = self.target[self.target["uploader"]]["rootdir_app"]
		self.target["rootdir_manifest"] = self.target[self.target["uploader"]]["rootdir_manifest"]
		return True
	
	def print(self):
		print("[INFO] Current Configuration:")

		print("[INFO] - Timetable engine: {}".format(self.timetable_engine))

		if self.timetable_engine == "www":
			print("[INFO] - Timetable URL: {}".format(self.timetable_url))
		elif self.timetable_engine == "vulcan":
			print("[INFO] - Vulcan login: {}".format(self.vulcan_login))
			print("[INFO] - Vulcan access: {}".format(self.vulcan_access))

		print("[INFO] - Overrides engine: {}".format(self.overrides_engine))

		if self.overrides_engine == "www":
			print("[INFO] - Overrides URL: {}".format(self.overrides_url))
		elif self.overrides_engine == "vulcan":
			print("[INFO] - Vulcan login: {}".format(self.vulcan_login))
			print("[INFO] - Vulcan access: {}".format(self.vulcan_access))

		if self.overrides_stats:
			print("[INFO] - Overrides stats: Enabled")
		else:
			print("[INFO] - Overrides stats: Disabled")

		if self.overrides_archiver:
			print("[INFO] - Overrides Archiver: Enabled")
		else:
			print("[INFO] - Overrides Archiver: Disabled")

		if self.timetable_archiver:
			print("[INFO] - Timetable Archiver: Enabled")
		else:
			print("[INFO] - Timetable Archiver: Disabled")

		if self.target['upload']:
			print("[INFO] - Upload: Enabled")
			print("[INFO] - Upload Module: {}".format(self.target['uploader']))
		else:
			print("[INFO] - Upload: Disabled")

		return True

