#coding: utf-8

timetable_url = "http://www.zseil.edu.pl/rnowa/html/"
timetable_engine = "www"
overrides_url = ""
overrides_engine = "www"

vulcan_login = ""
vulcan_password = ""

overrides_stats = True
overrides_archiver = True
timetable_archiver = True

ftp_upload = False
ftp_host = "127.0.0.1"
ftp_dir = "/polgesek.pl/dev/zseilplan/new_test"
ftp_user = "user"
ftp_password = "pass"


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