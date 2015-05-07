import json
import csv
import io

import config
import core.util.debug as debug

class DataEngineException(Exception):
	def __int__(self, message):
		self.message = message
	def __str__(self):
		return self.message

class DataEngine:

	def __init__(self, prices):
		try:
			self.data = self.validate(prices)
		except DataEngineException as e:
			debug.error('%s'%e)
			self.data = {}
		except Exception as e:
			self.data = {}

	def getPrices(self, progress):
		debug.error('DataEngine function not implemented')

	@staticmethod
	def validate(prices):
		debug.error('DataEngine function not implemented')


class JSONDataEngine(DataEngine):

	def getPrices(self, progress):
		res = {}
		for g in self.data:
			if isinstance(self.data[g], list):
				res[g] = self.data[g]
			else:
				res[g] = [self.data[g]]+[None]*7
		return res

	@staticmethod
	def validate(prices):

		if prices['data'] != None:
			data = json.loads(prices['data'])
		else:
			raise DataEngineException('Path based prices not (yet) supported')

		for k in data:
			if type(k) != str:
				raise DataEngineException('Keys must be strings')
			if type(data[k]) not in (int, list, float):
				raise DataEngineException('Values must be arrays or numbers')
			if type(data[k]) == list:
				if len(data[k]) > 8:
					raise DataEngineException('Array values must length of up to 8 items')
				if any(map(lambda i: type(i) not in [int, float], data[k])):
					raise DataEngineException('Array values must be all numbers')
		return data



class CSVDataEngine(DataEngine):


	def getPrices(self, progress):
		return self.data

	@staticmethod
	def validate(prices):
		raw = csv.reader(io.StringIO(prices['data'].strip()))
		data = {}

		for row in raw:
			if len(row) == 0:
				continue
			if len(row) > 2 or len(row) == 1:

				raise DataEngineException('Rows must have exactly 2 columns')
			if len(row) == 2:
				try:
					data[row[0].strip()] = [float(row[1])]+[None]*7
				except:
					raise DataEngineException('The first column must be a string, the second column must be a number')
		return data

class MetricCSVDataEngine(DataEngine):

	@staticmethod
	def validate(prices):
		raw = csv.reader(io.StringIO(prices['data'].strip()))
		rows = list(raw)

		if len(rows) < 2:
			raise DataEngineException('Must contain at least two rows')
		if len(rows[0]) < 2:
			raise DataEngineException('Must contain at least two columns')

		try:
			metric = rows[0][0]
			if 'metricString' in metric:
				metric = int(metric[12:])-1
			elif 'metricNumber' in metric:
				metric = int(metric[12:])+8-1
			else:
				assert(False)
			assert(metric<32 and metric>-1)
		except:
			raise DataEngineException('Metric name not valid/recognized')

		progress = list(map(lambda p: p.strip(), rows[0][1:]))
		data = dict(map(lambda p: (p.strip(), {}), rows[0][1:]))
		
		for row in rows[1:]:
			# Remove trailing spaces
			row = list(map(lambda r: r.strip(), row))

			if len(row) != len(row[0]):
				raise DataEngineException('All rows must contain the same number of elements')
			
			for i, value in enumerate(row[1:]):
				try:
					data[progress[i]][row[0]] = [float(value)] + [None]*7
				except:
					raise DataEngineException('The first column must be a tring, all other columns must be good prices encoded as numbers')

		return {'metric':metric, 'data':data}




class ApplicationNotFoundException(Exception):
	def __str__(self):
		return 'No application found given the application key'

class NoPricingForGroup(Exception):
	def __str__(self):
		return 'Application has no defined prices for group'


class PricingEngine:


	def __init__(self, application_key):
		import core.content.content as content
		backend = content.Content()

		self.groupAPrices = None
		self.groupBPrices = None

		self.abtest = backend.getABTest(application_key)
		
		# If there is no AB test for application.. we are done
		if self.abtest == None:
			raise ApplicationNotFoundException()
		
		self.abtest = self.abtest.as_dict()

		if self.abtest['groupAPrices_key'] != None:
			self.groupAPrices = self.__loadPrices(self.abtest['groupAPrices_key'])
		
		if self.abtest['groupBPrices_key'] != None:
			self.groupBPrices = self.__loadPrices(self.abtest['groupBPrices_key'])


	def getPrices(self, user, progress):
		
		userID = int(user, 16)
		
		if userID % self.abtest['modulus'] <= self.abtest['modulusLimit']:
			if self.groupAPrices:
				return self.groupAPrices.getPrices(progress)
			else:
				raise NoPricingForGroup()
		else:
			if self.groupBPrices:
				return self.groupBPrices.getPrices(progress)
			else:
				raise NoPricingForGroup()

		return None

	def __loadPrices(self, prices_key):
		import core.content.content as content
		backend = content.Content()

		data = backend.getPrice(prices_key).as_dict()

		if data['engine'] == 'JSON':
			return JSONDataEngine(data)
		elif data['engine'] == 'CSV':
			return CSVDataEngine(data)
		elif data['engine'] == 'MetricCSV':
			return MetricCSVDataEngine(data)

		return None