from PIL import Image, ImageDraw, ImageColor
import random, sys, math, pdb



class ImageWorker:
	orient = [(-1, 0), (0, -1), (-1, -1), (1, -1)]
	def __init__(self, filename, threshold, neighborhood):
		try:
			self.image = Image.open(filename)
		except IOError:
			print("File not found")
			exit(0)
		self.draw = ImageDraw.Draw(self.image)
		self.width = self.image.size[0]
		self.height = self.image.size[1]
		self.pix = self.image.load()
		self.grayMatrix = []
		for x in range(self.width):
			self.grayMatrix.append([0 for x in range(self.height)])

		self.regionCount = 0
		self.mode = int(neighborhood)
		self.threshold = int(threshold) 
		self.stack = []
		self.ThresholdDict = {}
		self.region_amount ={}

	def howMuch(self):
		print(self.regionCount)

	def redefineThreshold(self, forRegion):
		self.ThresholdDict[forRegion] = max(self.threshold - math.floor(self.region_amount[forRegion]/5), 2)
		

	# def printThresh(self):
	# 	for key in self.ThresholdDict:
	# 		print("{0} : {1}".format(key, self.ThresholdDict[key]))




	def makeGray(self):
		for i in range(self.width):
			for j in range(self.height):
				a = self.pix[i,j][0]
				b = self.pix[i,j][1]
				c = self.pix[i,j][2]
				S = int(a*0.299 + b*0.587 + c*0.114)
				self.grayMatrix[i][j] = (S, 0)
		return self.grayMatrix

	def startRegionGrow(self):
		for i in range(self.height):
			for j in range(self.width):
				self.checkConnectivity(j, i)

	def createNewRegion(self, coord1, coord2):
		self.regionCount+=1
		self.grayMatrix[coord1][coord2] = (self.grayMatrix[coord1][coord2][0], self.regionCount)
		self.region_amount[self.regionCount] = 1
		self.redefineThreshold(self.regionCount)
		

	def checkConnectivity(self, coord1, coord2):
		
		deltaDict = {}

		if self.mode == 4:
			self.orient = self.orient[:2]
		for item in self.orient:
			ix = item[0]
			iy = item[1]
			if coord1+ix < 0 or coord1+ix > self.width-1 or coord2+iy < 0:
				pass
			else:
				delta = abs(self.grayMatrix[coord1+ix][coord2+iy][0]-self.grayMatrix[coord1][coord2][0])
				deltaDict[item] = delta

		if len(deltaDict) == 0:
			self.createNewRegion(coord1, coord2)
			return

		minkey = min(deltaDict, key=deltaDict.get) #выбираем ключ с наименьшей дельтой
		ix = minkey[0]
		iy = minkey[1]
		try:
			t1 = self.ThresholdDict[self.grayMatrix[coord1][coord2][1]]
		except:
			t1 = self.threshold
		t2 = self.ThresholdDict[self.grayMatrix[coord1+ix][coord2+iy][1]]
		
		if deltaDict[minkey] <= min(t1, t2):	
			reg = self.grayMatrix[coord1+ix][coord2+iy][1]
			self.grayMatrix[coord1][coord2] = (self.grayMatrix[coord1][coord2][0], reg)
			self.region_amount[reg]+=1
			self.redefineThreshold(reg)

			del deltaDict[minkey]
			self.checkRegions(deltaDict, (coord1, coord2))

		else:
			self.createNewRegion(coord1, coord2)

	def mergeRegions(self, mergePoint, basePoint):
		m = self.grayMatrix[mergePoint[0]][mergePoint[1]][1]
		s = self.grayMatrix[basePoint[0]][basePoint[1]][1]
		main = mergePoint
		second = basePoint

		if self.region_amount[m] < self.region_amount[s]:
			main, second = second, main

		regTo = self.grayMatrix[main[0]][main[1]][1]
		regFrom = self.grayMatrix[second[0]][second[1]][1]

		if regTo == regFrom:
			return

		self.stack.append(second)
		self.actualMerge(second, regFrom, regTo)

	
	def actualMerge(self, nextPoint, regFrom, regTo):
		coord1 = nextPoint[0]
		coord2 = nextPoint[1]
		self.grayMatrix[coord1][coord2] = (self.grayMatrix[coord1][coord2][0], regTo)
		self.addPoint(nextPoint, regFrom, regTo)
		while len(self.stack) != 0:

			#pdb.set_trace()
			elem = self.stack.pop()
			self.addPoint(elem, regFrom, regTo)			

	def addPoint(self, nextPoint, regFrom, regTo):
		radius = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]
		coord1 = nextPoint[0]
		coord2 = nextPoint[1]
		
		for item in radius:
			ix = item[0]
			iy = item[1]
			if coord1+ix < 0 or coord1+ix > self.width-1 or coord2+iy < 0 or self.grayMatrix[coord1+ix][coord2+iy][1]!= regFrom:
				pass
			else:
				self.grayMatrix[coord1+ix][coord2+iy] = (self.grayMatrix[coord1+ix][coord2+iy][0], regTo)
				self.stack.append((coord1+ix, coord2+iy))

			

	def checkRegions(self, ndict, basePoint):
		coord1 = basePoint[0]
		coord2 = basePoint[1]
		for key in ndict:
			ix = key[0]
			iy = key[1]
			t1 = self.ThresholdDict[self.grayMatrix[coord1][coord2][1]]
			t2 = self.ThresholdDict[self.grayMatrix[coord1+ix][coord2+iy][1]]
			if abs(self.grayMatrix[coord1+ix][coord2+iy][0]-self.grayMatrix[coord1][coord2][0]) < min(t1, t2):
				self.mergeRegions((coord1+ix, coord2+iy), basePoint)
	

	def generateColors(self, count):
		AllColors = [x for x in ImageColor.colormap]
		#delim = len(AllColors)// count
		#resultList = [ImageColor.getrgb(AllColors[delim*x]) for x in range(count)]

		return AllColors

	def drawImage(self):
		colors = self.generateColors(self.regionCount)
		regColors = [ ImageColor.getrgb(  colors[ int(random.random() * len(colors)) ] )  for x in range(self.regionCount)]
		for i in range(self.width):
			for j in range(self.height):
				reg = self.grayMatrix[i][j][1]
				self.draw.point((i,j), regColors[reg-1])			
					

	




	# def findBigRegions
						
			
	def StartAll(self):
		self.makeGray()
		# self.printThresh()
		self.startRegionGrow()
		self.howMuch()
		self.drawImage()
		self.image.show()

if len(sys.argv) < 4:
	print ('Usage : python .py filename threshold neighborhood')
	sys.exit()
if True != (int(sys.argv[3])== 4 or int(sys.argv[3])== 8):
	print ('wrong neighborhood. Use only 4 or 8')
	sys.exit()

some = ImageWorker(sys.argv[1], sys.argv[2], sys.argv[3])
some.StartAll()


