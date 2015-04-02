import unittest
import json
import requests
import sys
import string
import random

import config
import service.api.errors as errors
import service.api.main as main
from util.test import *

def genRandomStrings(count, length):
	return map(lambda c: ''.join(map(lambda i: random.choice(string.ascii_uppercase), range(length))), range(count))

class TestGame(APITest):

	def testAdd(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		self.assertEqual(a['name'], 'Test game')

	def testAddGet(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('GET', '/games/get/v1/', {'key': a['key']})
		self.assertEqual(a['name'], b['name'])
		self.assertEqual(a['key'], b['key'])
		self.assertEqual(a['created'], b['created'])

	def testAddDeleteGet(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('DELETE', '/games/delete/v1/', {'key': a['key']})
		self.assertEqual(b['deleted'], True)

	def testList(self):
		(status, a) = self.request('GET', '/games/list/v1/', {})
		(status, b) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, c) = self.request('GET', '/games/list/v1/', {})
		self.assertEqual(len(a['games']), len(c['games'])-1)
		for game in c['games']:
			self.request('DELETE', '/games/delete/v1/', {'key': game['key']})
		(status, d) = self.request('GET', '/games/list/v1/', {})
		self.assertEqual(len(d['games']), 0)
		
	def testUpdate(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('PUT', '/games/update/v1/', {'key': a['key'], 'name': 'The new name'})
		(status, c) = self.request('GET', '/games/get/v1/', {'key': a['key']})
		self.assertEqual(c['name'], b['name'])

	# Get game with wrong key
	def testBadKey(self):
		(status, a) = self.request('GET', '/games/get/v1/', {'key': ''})
		self.assertEqual(status, errors.GameKeyDoesNotExist['status'])

	# Delete game with wrong key
	def testDeleteBadKey(self):
		(status, a) = self.request('DELETE', '/games/delete/v1/', {'key': ''})
		self.assertEqual(status, errors.GameKeyDoesNotExist['status'])

	# Update game with wrong key
	def testUpdateWithBadKey(self):
		(status, a) = self.request('PUT', '/games/update/v1/', {'key': '', 'name': 'The new name'})
		self.assertEqual(status, errors.GameKeyDoesNotExist['status'])


class TestCurrency(APITest):

	def testUpdateCurrency(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		
		values = genRandomStrings(8, 8)

		for i, v in enumerate(values):
			(status, b) = self.request('PUT', '/currencies/update/v1/', {'key': a['key'], 'name%d'%(i+1):v})
		(status, c) = self.request('GET', '/currencies/get/v1/', {'key': a['key']})
		
		for i, v in enumerate(values):
			self.assertEqual(c['name%d'%(i+1)], v)
		
	def testUpdateCurrencyWithBadKey(self):
		(status, c) = self.request('GET', '/currencies/get/v1/', {'key': ''})
		self.assertEqual(status, errors.GameKeyDoesNotExist['status'])

class TestMetrics(APITest):

	def testUpdateMetrics(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		
		# Strings
		values = genRandomStrings(8, 8)
		for i, v in enumerate(values):
			(status, b) = self.request('PUT', '/metrics/update/v1/', {'key': a['key'], 'str%d'%(i+1):v})
		(status, c) = self.request('GET', '/metrics/get/v1/', {'key': a['key']})
		for i, v in enumerate(values):
			self.assertEqual(c['str%d'%(i+1)], v)
		
		# Numbers
		values = genRandomStrings(24, 8)
		for i, v in enumerate(values):
			(status, b) = self.request('PUT', '/metrics/update/v1/', {'key': a['key'], 'num%d'%(i+1):v})
		(status, c) = self.request('GET', '/metrics/get/v1/', {'key': a['key']})
		for i, v in enumerate(values):
			self.assertEqual(c['num%d'%(i+1)], v)	

	def testUpdateMetricsWithBadKey(self):
		(status, c) = self.request('GET', '/metrics/get/v1/', {'key': ''})
		self.assertEqual(status, errors.GameKeyDoesNotExist['status'])

class TestGoods(APITest):

	def testAddAndGetGood(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('POST', '/goods/add/v1/', {'key': a['key'], 'name':'Sword'})
		(status, c) = self.request('GET', '/goods/get/v1/', {'key': b['key']})
		self.assertEqual(b['name'], 'Sword')
		self.assertEqual(b['game_key'], a['key'])
		self.assertEqual(c['name'], b['name'])
		self.assertEqual(c['key'], b['key'])
		self.assertEqual(c['game_key'], b['game_key'])

	def testDeleteGood(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('POST', '/goods/add/v1/', {'key': a['key'], 'name':'Sword'})
		(status, c) = self.request('DELETE', '/goods/delete/v1/', {'key': b['key']})

		self.assertEqual(c['deleted'], True)

	def testListGoods(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('GET', '/goods/list/v1/', {'key': a['key']})
		(status, c) = self.request('POST', '/goods/add/v1/', {'key': a['key'], 'name':'Sword'})
		(status, d) = self.request('GET', '/goods/list/v1/', {'key': a['key']})
		self.assertEqual(len(b['goods']), len(d['goods'])-1)

	def testUpdateGood(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('POST', '/goods/add/v1/', {'key': a['key'], 'name':'Sword'})
		(status, c) = self.request('PUT', '/goods/update/v1/', {'key': b['key'], 'name':'Sword 2'})

		self.assertEqual(c['name'], 'Sword 2')

	def testGetGoodWithBadKey(self):
		(status, c) = self.request('GET', '/goods/get/v1/', {'key': ''})
		self.assertEqual(status, errors.GoodKeyDoesNotExist['status'])

	def testGetGameGoodsWithBadKey(self):
		(status, c) = self.request('GET', '/goods/list/v1/', {'key': ''})
		self.assertEqual(len(c['goods']), 0)

class TestPrices(APITest):

	def testAddAndGetPrice(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('POST', '/prices/add/v1/', {'key': a['key'], 'engine':'JSON', 'data':'{}', 'path':None})
		(status, c) = self.request('GET', '/prices/get/v1/', {'key': b['key']})

		self.assertEqual(b['engine'], 'JSON')
		self.assertEqual(b['game_key'], a['key'])
		self.assertEqual(b['data'], '{}')
		self.assertEqual(b['path'], None)

		self.assertEqual(b['engine'], c['engine'])
		self.assertEqual(b['game_key'],c['game_key'])
		self.assertEqual(b['data'], c['data'])
		self.assertEqual(b['path'], c['path'])

	def testDeletePrices(self):

		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('POST', '/prices/add/v1/', {'key': a['key'], 'engine':'JSON', 'data':'{}', 'path':None})
		(statuc, c) = self.request('DELETE', '/prices/delete/v1/', {'key': b['key']})

		self.assertEqual(c['deleted'], True)

	def testListPrices(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('GET', '/prices/list/v1/', {'key': a['key']})
		(status, c) = self.request('POST', '/prices/add/v1/', {'key': a['key'], 'engine':'JSON', 'data':'{}', 'path':None})
		(status, d) = self.request('GET', '/prices/list/v1/', {'key': a['key']})
		self.assertEqual(len(b['prices']), len(d['prices'])-1)

	def testGetPriceWithBadKey(self):
		(status, b) = self.request('GET', '/prices/get/v1/', {'key': ''})
		self.assertEqual(status, errors.PricesKeyDoesNotExist['status'])

class TestABTest(APITest):

	def testGetABTest(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('GET', '/abtest/get/v1/', {'key': a['key']})

		self.assertEqual(b['game_key'], a['key'])
		self.assertEqual(b['dynamicPrices_key'], None)
		self.assertEqual(b['staticPrices_key'], None)
		self.assertEqual(b['countryWhiteList'], '')
		self.assertEqual(b['countryBlackList'], '')
		self.assertEqual(b['modulus'], 2)
		self.assertEqual(b['modulusLimit'], 0)

	def testUpdateABTest(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('GET', '/abtest/get/v1/', {'key': a['key']})
		(status, c) = self.request('PUT', '/abtest/update/v1/', {'key': a['key'], 'countryWhiteList':'BR', 'countryBlackList':'PT', 'modulus': 6, 'modulusLimit': 3})

		self.assertEqual(c['game_key'], a['key'])
		self.assertEqual(c['dynamicPrices_key'], None)
		self.assertEqual(c['staticPrices_key'], None)
		self.assertEqual(c['countryWhiteList'], 'BR')
		self.assertEqual(c['countryBlackList'], 'PT')
		self.assertEqual(c['modulus'], 6)
		self.assertEqual(c['modulusLimit'], 3)

	def testUpdateABTestPrices(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('POST', '/prices/add/v1/', {'key': a['key'], 'engine':'JSON', 'data':'{}', 'path':None})
		(status, c) = self.request('PUT', '/abtest/update/v1/', {'key': a['key'], 'dynamicPrices_key':b['key']})
		self.assertEqual(c['dynamicPrices_key'], b['key'])
	
	def testUpdateABTestBadPrices(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('PUT', '/abtest/update/v1/', {'key': a['key'], 'dynamicPrices_key':'12134'})
		(status, c) = self.request('GET', '/abtest/get/v1/', {'key': a['key']})
		(status, d) = self.request('PUT', '/abtest/update/v1/', {'key': a['key'], 'staticPrices_key':'12134'})
		(status, e) = self.request('GET', '/abtest/get/v1/', {'key': a['key']})
		self.assertEqual(c['dynamicPrices_key'], None)
		self.assertEqual(e['staticPrices_key'], None)

	def testDeletePrices(self):
		(status, a) = self.request('POST', '/games/add/v1/', {'name': 'Test game'})
		(status, b) = self.request('POST', '/prices/add/v1/', {'key': a['key'], 'engine':'JSON', 'data':'{}', 'path':None})
		(status, c) = self.request('PUT', '/abtest/update/v1/', {'key': a['key'], 'dynamicPrices_key':b['key']})
		(status, d) = self.request('GET', '/abtest/get/v1/', {'key': a['key']})
		(status, e) = self.request('DELETE', '/prices/delete/v1/', {'key': b['key']})
		(status, f) = self.request('GET', '/abtest/get/v1/', {'key': a['key']})

		# Fail to delete price when being used in an AB Test
		self.assertEqual(e['deleted'], 0)
		self.assertEqual(f['dynamicPrices_key'], b['key'])
		self.assertEqual(c['dynamicPrices_key'], b['key'])

		# Delete of price works when price not being used in an AB Test
		(status, g) = self.request('PUT', '/abtest/update/v1/', {'key': a['key'], 'dynamicPrices_key':None})
		self.assertEqual(g['dynamicPrices_key'], None)
		(status, h) = self.request('DELETE', '/prices/delete/v1/', {'key': b['key']})
		self.assertEqual(h['deleted'], True)


suite = unittest.TestSuite()

# Tests without testing server
suite.addTests(discoverTests(TestGame, config.APIAddress, config.APIPort, main.app))
suite.addTests(discoverTests(TestCurrency, config.APIAddress, config.APIPort, main.app))
suite.addTests(discoverTests(TestMetrics, config.APIAddress, config.APIPort, main.app))
suite.addTests(discoverTests(TestGoods, config.APIAddress, config.APIPort, main.app))
suite.addTests(discoverTests(TestPrices, config.APIAddress, config.APIPort, main.app))
suite.addTests(discoverTests(TestABTest, config.APIAddress, config.APIPort, main.app))

# Tests using server
# suite.addTests(discoverTests(TestGame, config.APIAddress, config.APIPort))
# suite.addTests(discoverTests(TestCurrency, config.APIAddress, config.APIPort))
# suite.addTests(discoverTests(TestMetrics, config.APIAddress, config.APIPort))
# suite.addTests(discoverTests(TestGoods, config.APIAddress, config.APIPort))
# suite.addTests(discoverTests(TestPrices, config.APIAddress, config.APIPort))
# suite.addTests(discoverTests(TestABTest, config.APIAddress, config.APIPort))

unittest.TextTestRunner(verbosity=2).run(suite)
