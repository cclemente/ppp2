
import wx
import numpy as np
from matplotlib import pyplot
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure






class MatplotlibPanel(wx.Panel):
	def __init__(self,parent,ID=-1,label="",pos=wx.DefaultPosition,size=(100,25)):
		self.parent = parent
		#(0) Initialize panel:
		wx.Panel.__init__(self,parent,ID,pos,size,wx.STATIC_BORDER,label)
		self.SetMinSize(size)
		self.parent = parent
		#(1) Create Matplotlib figure:
		self.figure = Figure(facecolor=(0.8,)*3)
		self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
		self._resize()
		self._create_axes()
		self.cidAxisEnter   = self.canvas.mpl_connect('axes_enter_event', self.callback_enter_axes)
		self.cidAxisLeave   = self.canvas.mpl_connect('axes_leave_event', self.callback_leave_axes)
		#self.Bind(wx.EVT_ENTER_WINDOW, self.callback_enter_axes)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.callback_leave_axes)
		
	def _create_axes(self):
		self.ax = self.figure.add_axes((0,0,1,1), axisbg=[0.5]*3)
		pyplot.setp(self.ax, xticks=[], yticks=[])

	def _resize(self):
		szPixels = tuple( self.GetClientSize() )
		self.canvas.SetSize(szPixels)
		szInches = float(szPixels[0])/self.figure.get_dpi() ,  float(szPixels[1])/self.figure.get_dpi()
		self.figure.set_size_inches( szInches[0] , szInches[1] )
	
	
        def callback_enter_axes(self, event):
                self.parent.parent.panel_enter(event, panel=self.parent)
	def callback_leave_axes(self, event):
	 	self.parent.parent.panel_leave(event)
	
	
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




class TemplateSingleStepPanel(wx.Panel):
	def __init__(self,parent,ID=-1,label="",pos=wx.DefaultPosition,size=(100,25)):
		wx.Panel.__init__(self,parent,ID,pos,size,wx.STATIC_BORDER,label)
		self.parent = parent
		self.SetMinSize(size)
		#Create layout:
		self.panelMatplotlib = MatplotlibPanel(self, size=(200,300))
		self.text            = wx.StaticText(self, label='0 of 0', pos=(10, 10))
		self.button_back     = wx.Button(self, -1, '<',  (50, 100))
		self.button_forward  = wx.Button(self, -1, '>',  (50, 100))
		sizer                = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.button_back, 1, flag=wx.ALL)
		sizer.Add(self.button_forward, 1, flag=wx.ALL)
		sizer_Main = wx.BoxSizer(wx.VERTICAL)
		sizer_Main.Add(self.panelMatplotlib, 6, flag=wx.CENTER)
		sizer_Main.Add(sizer, 1, flag=wx.EXPAND)
		sizer_Main.Add(self.text, 1, flag=wx.CENTER)
		self.SetSizer(sizer_Main)
		self.Fit()
		# self.Centre()
		self.button_back.Bind(wx.EVT_BUTTON, self.callback_back)
		self.button_forward.Bind(wx.EVT_BUTTON, self.callback_forward)
		#self.Bind(wx.EVT_ENTER_WINDOW, self.callback_enter_axes)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.callback_leave_axes)
		
	
	def callback_back(self, event):
		self.parent.update(self, -1)
	def callback_forward(self, event):
		self.parent.update(self, +1)

	
	def callback_enter_axes(self, event):
		self.parent.panel_enter(event)
	def callback_leave_axes(self, event):
		self.parent.panel_leave(event)	
	
	def cla(self):
		self.panelMatplotlib.cla()
	
	def plot(self, I, cmax=None):
		self.panelMatplotlib.plot(I, cmax)
		


	