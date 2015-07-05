from PIL import Image, ImageDraw, ImageColor
import random, sys



class ImageWorker:
	orient = [(1, 0), (0, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
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
		self.mode = neighborhood
		self.threshold = int(threshold) # граница
		self.stack = []

	def howMuch(self):
		print(self.regionCount)

	def makeGray(self):
		for i in range(self.width):
			for j in range(self.height):
				a = self.pix[i,j][0]
				b = self.pix[i,j][1]
				c = self.pix[i,j][2]
				S = int(a*0.299 + b*0.587 + c*0.114)
				self.grayMatrix[i][j] = (S, 0)
		return self.grayMatrix

	def findNewRegion(self):
		for i in range(self.width):
			for j in range(self.height):
				if self.grayMatrix[i][j][1] != 0:
					pass
				else:
					self.regionCount+=1
					self.createRegion(i, j)

	def createRegion(self, coord1, coord2):
		self.grayMatrix[coord1][coord2] = (self.grayMatrix[coord1][coord2][0], self.regionCount)
		self.checkConnectivity(coord1, coord2)
		while len(self.stack) != 0:
			elem = self.stack.pop()
			self.checkConnectivity(elem[0], elem[1])			

	def checkConnectivity(self, coord1, coord2):
		
		count = 0

		#valueOfArea = self.criteria(coord1, coord2)

		if self.mode == "four":
			self.orient = self.orient[:4]
		for item in self.orient:
			ix = item[0]
			iy = item[1]
			if coord1+ix < 0 or coord1+ix > self.width-1 or coord2+iy < 0 or coord2+iy > self.height-1 or self.grayMatrix[coord1+ix][coord2+iy][1]==self.regionCount:
				pass
			else:
				if self.grayMatrix[coord1+ix][coord2+iy][1] == 0 and abs(self.grayMatrix[coord1+ix][coord2+iy][0] - self.grayMatrix[coord1][coord2][0]) < self.threshold:
					self.grayMatrix[coord1+ix][coord2+iy] = (self.grayMatrix[coord1+ix][coord2+iy][0], self.regionCount)
					self.stack.append((coord1+ix, coord2+iy))

	def criteria(self, coord1, coord2):
		val = 0
		delit = 1
		# if self.mode == "four":
		# 	self.orient = self.orient[:4]

		for item in self.orient:
			ix = item[0]
			iy = item[1]
			if coord1+ix < 0 or coord1+ix > self.width-1 or coord2+iy < 0 or coord2+iy > self.height-1:
				pass
			else:
				if self.grayMatrix[coord1+ix][coord2+iy][1] == self.grayMatrix[coord1][coord2][1]:
					val+= self.grayMatrix[coord1+ix][coord2+iy][0]
					delit+=1

		return float(val/delit)

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
				#if self.grayMatrix[i][j][0]> 20:
				reg = self.grayMatrix[i][j][1]
				self.draw.point((i,j), regColors[reg-1])			
					

	




	# def findBigRegions
						
			
	def StartAll(self):
		self.makeGray()
		self.findNewRegion()
		self.howMuch()
		self.drawImage()
		self.image.show()

if len(sys.argv) < 4:
	print ('Usage : python .py filename threshold neighborhood')
	sys.exit()

some = ImageWorker(sys.argv[1], sys.argv[2], sys.argv[3])
some.StartAll()


