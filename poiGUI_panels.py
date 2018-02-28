
import wx
import numpy as np
from matplotlib import pyplot
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure






class MatplotlibPanel(wx.Panel):
	def __init__(self,parent,ID=-1,label="",pos=wx.DefaultPosition,size=(100,25), panelnum=0):
		#(0) Initialize panel:
		wx.Panel.__init__(self,parent,ID,pos,size,wx.STATIC_BORDER,label)
		self.SetMinSize(size)
		self.parent = parent
		self.panelnum = panelnum
		#(1) Create Matplotlib figure:
		self.figure = Figure(facecolor=(0.8,)*3)
		self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
		self._resize()
		self._create_axes()
		self.cidButtonDown  = self.canvas.mpl_connect('button_press_event', self.callback_button_press)
		
	def _create_axes(self):
		self.ax = self.figure.add_axes((0,0,1,1), axisbg=[0.5]*3)
		pyplot.setp(self.ax, xticks=[], yticks=[])

	def _resize(self):
		szPixels = tuple( self.GetClientSize() )
		self.canvas.SetSize(szPixels)
		szInches = float(szPixels[0])/self.figure.get_dpi() ,  float(szPixels[1])/self.figure.get_dpi()
		self.figure.set_size_inches( szInches[0] , szInches[1] )
	
	
	def callback_button_press(self, event):
		xy    = event.xdata, event.ydata
		shift = event.guiEvent.m_shiftDown
		if xy != (None,None):
			xy = tuple(   np.round(xy, decimals=1)   )
			if event.button==1:
				if shift:
					self.parent.poi_select(xy, self.panelnum)
				else:  #add POI
					self.parent.poi_add(xy, self.panelnum)
			else:  #delete closest POI
				self.parent.poi_delete(xy, self.panelnum)
	
	def cla(self):
		self.ax.cla()
		self.ax.set_position([0,0,1,1])
		self.ax.set_axis_bgcolor([0.5]*3)
		pyplot.setp(self.ax, xticks=[], yticks=[], xlim=(0,1), ylim=(0,1))
		self.ax.axis('tight')
		self.canvas.draw()
	
	def plot(self, I, cmax=None):
		if I!=None:
			if cmax==None:
				cmax = I.max()
			I[I==0] = np.nan
			self.ax.imshow(I, interpolation='nearest', origin='lower', vmin=0, vmax=cmax)
			pyplot.setp(self.ax, xticks=[], yticks=[])
			self.ax.set_axis_bgcolor([0.05]*3)
			self.ax.axis('image')
		self.canvas.draw()
		
	def highlight_poi(self, ind):
		for i,line in enumerate(self.ax.lines):
			if i==ind:
				pyplot.setp(line, color='g', markersize=12)
			else:
				pyplot.setp(line, color='w', markersize=8)
		self.canvas.draw()

	
	def plot_poi(self, xy):
		x,y = xy
		i   = len(self.ax.texts) + 1
		self.ax.plot(x, y, 'wo', markersize=8)
		self.ax.text(x+1, y+1, '%d'%i, bbox=dict(facecolor='w'))
		
	def replot_pois(self, pois):
		self.ax.lines = []
		self.ax.texts = []
		if pois:
			[self.plot_poi(xy)  for xy in pois]
		self.canvas.draw()





	