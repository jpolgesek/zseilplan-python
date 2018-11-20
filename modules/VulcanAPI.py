#coding: UTF-8
import requests
import json
import datetime

from lxml.html import fromstring
from lxml.etree import tostring as htmlstring

class VulcanAPI:
	def __init__(self):
		self.schoolID = "warszawazoliborz"
		self.login_endpoint = "https://uonetplus-uzytkownik.vulcan.net.pl/{}/LoginEndpoint.aspx".format(self.schoolID)
		self.cufs_url = "https://cufs.vulcan.net.pl/{0}/Account/LogOn?ReturnUrl=%2Fwarszawazoliborz%2FFS%2FLS%3Fwa%3Dwsignin1.0%26wtrealm%3D{1}%26wctx%3D{1}".format(self.schoolID, self.login_endpoint)


		# Requests config #
		self.check_ssl = True
		self.proxy_enabled = False

		if self.proxy_enabled:
			self.proxies = {
				'http': 'http://127.0.0.1:8080',
				'https': 'http://127.0.0.1:8080',
			}
		else:
			self.proxies = {}

		self.token_data = {}
		self.session = requests.Session()
		return None
	
	def login(self, username, password):
		#Returns:
		#  true on success, 
		#  false on any error

		r = self.session.post(self.cufs_url, 
							data = {'LoginName':username,"Password":password}, 
							proxies=self.proxies, verify=self.check_ssl )
		
		if r.text.find("Zła nazwa użytkownika lub hasło") != -1:
			return False
		
		innerTree = fromstring(r.text)
		innerTree = innerTree[1][0]

		saml_form = {}
		saml_form['wa'] = innerTree.xpath('//input[@name="wa"]/@value')
		saml_form['wresult'] = innerTree.xpath('//input[@name="wresult"]/@value')
		saml_form['wctx'] = innerTree.xpath('//input[@name="wctx"]/@value')

		url = "https://uonetplus-uzytkownik.vulcan.net.pl/warszawazoliborz/LoginEndpoint.aspx"
		
		r = self.session.post(url, data = saml_form, proxies=self.proxies, verify=self.check_ssl)
		r.encoding = "UTF-8"
		temp = r.text
		temp = temp[temp.find("var VParam = {")+14:temp.find(" };")]
		
		for line in temp.split("\n"):
			if line.find(":") == -1:
				continue
			line = line.split(": ")
			key = line[0].strip()
			value = line[1].strip()
			value = value[1:-2] # 'test', => test
			self.token_data[key] = value
			#print("{} = {}".format(key, value))
		
		# print ("CSRFtoken:", self.token_data['antiForgeryToken'])
		# print ("GUID:", self.token_data['appGuid'])

		# If nothing failed, we should have a working session
		return True

	def get_timetable(self, timeDelta = 0):
		if timeDelta >= 7:
			return False

		url = "https://uonetplus-administracja.vulcan.net.pl/warszawazoliborz/002200/PlanLekcji.mvc/GetContext"
		
		weekStart = datetime.datetime.today() - datetime.timedelta(days=datetime.datetime.today().isoweekday() % 7) + datetime.timedelta(weeks = timeDelta)
		weekEnd = weekStart + datetime.timedelta(days = 7)

		weekStart = weekStart.strftime("%Y-%m-%dT00:00:00")
		weekEnd = weekEnd.strftime("%Y-%m-%dT00:00:00")

		json = {
			"dataOd": weekStart,
			"dataDo": weekEnd,
			"data": weekStart,
		}

		headers = {
			"x-requested-with": "XMLHttpRequest",
			"x-v-appguid": "a63ae78e454406991bfc50a039eaa546",
			"x-v-requestverificationtoken": self.token_data['antiForgeryToken'],
		}

		r = self.session.post(url, json=json, headers=headers)

		if r.status_code != 200:
			print("get_timetable() status code not 200: {}".format(r.status_code))
		
		try:
			data = r.json()
			return data
		except:
			return False