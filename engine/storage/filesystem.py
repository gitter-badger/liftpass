import uuid
import os

from engine.storage import Storage
import config


class Filesystem(Storage):

	def __init__(self):
		print('[%s] Init'%self)
		

	def save(self, data, datatype = 'json'):
		filename = '%s/%s.%s'%(config.StoragePath, uuid.uuid4().hex, datatype)
		f = open(filename, 'w+')
		f.write(data)
		f.close()
		

	def count(self):
		return len(os.listdir(config.StoragePath))


	def __repr__(self):
		return 'Filesystem'