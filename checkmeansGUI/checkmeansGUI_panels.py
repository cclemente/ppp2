
import wx
import numpy as np
from matplotlib import pyplot
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure






class CheckMeansPanel(wx.Panel):
	def __init__(self,parent,ID=-1,label="",pos=wx.DefaultPosition,size=(100,25)):
		#(0) Initialize panel:
		wx.Panel.__init__(self,parent,ID,pos,size,wx.STATIC_BORDER,label)
		self.SetMinSize(size)
		#(1) Create Matplotlib figure:
		self.figure = Figure(facecolor=(0.8,)*3)
		self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
		self._resize()
		self._create_axes()
		# self.cidAxisEnter   = self.canvas.mpl_connect('axes_enter_event', self.callback_enter_axes)
		# self.cidAxisLeave   = self.canvas.mpl_connect('axes_leave_event', self.callback_leave_axes)
		
	def _create_axes(self):
		self.ax  = self.figure.add_axes((0,0,1,1), axisbg=[0.5]*3)
		self.cax = self.figure.add_axes((0.1,0.05,0.8,0.02), axisbg=[0.5]*3)
		pyplot.setp(self.ax, xticks=[], yticks=[])

	def _resize(self):
		szPixels = tuple( self.GetClientSize() )
		self.canvas.SetSize(szPixels)
		szInches = float(szPixels[0])/self.figure.get_dpi() ,  float(szPixels[1])/self.figure.get_dpi()
		self.figure.set_size_inches( szInches[0] , szInches[1] )
		
	
	# def callback_enter_axes(self, event):
	# 	print 'buta-san in'
	# def callback_leave_axes(self, event):
	# 	print 'buta-san out'
	
	def cla(self):
		self.ax.cla()
		self.cax.cla()
		# self.ax.set_position([0,0,1,1])
		self.ax.set_axis_bgcolor([0.5]*3)
		pyplot.setp(self.ax, xticks=[], yticks=[], xlim=(0,1), ylim=(0,1))
		self.ax.axis('tight')
		self.canvas.draw()
	
	def plot(self, I):
		I = np.asarray(I, dtype=float)
		I[I==0] = np.nan
		self.ax.imshow(I, interpolation='nearest', origin='lower')
		pyplot.setp(self.ax, xticks=[], yticks=[])
		self.ax.set_axis_bgcolor([0.05]*3)
		self.ax.axis('image')
		cb = pyplot.colorbar(cax=self.cax, mappable=self.ax.images[0], orientation='horizontal')
		pyplot.setp(cb.ax.get_xticklabels(), color='0.5')
		self.canvas.draw()






	