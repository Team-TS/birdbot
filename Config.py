import yaml
from os import path

class Config:
	"""Object for holding config variables"""
	token = ""

	def __init__(self):
		with open(path.join("config/", "config.yml")) as ymlfile:
			read = yaml.load(ymlfile)
		
		Config.token = read["discord"]["token"]