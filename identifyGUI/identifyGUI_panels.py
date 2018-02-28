
import wx
import numpy as np
from matplotlib import pyplot
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure






class IdentifyMatplotlibPanel(wx.Panel):
	def __init__(self,parent,ID=-1,label="",pos=wx.DefaultPosition,size=(100,25)):
		#(0) Initialize panel:
		wx.Panel.__init__(self,parent,ID,pos,size,wx.STATIC_BORDER,label)
		self.SetMinSize(size)
		#(1) Create Matplotlib figure:
		self.figure = Figure(facecolor=(0.8,)*3)
		self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
		self._resize()
		self._create_axes()
		
	def _create_axes(self):
		self.ax = self.figure.add_axes((0,0,1,1), axisbg=[0.5]*3)
		# self.plot(None)
		# self.ax.plot( np.random.randn(10) )
		pyplot.setp(self.ax, xticks=[], yticks=[])

	def _resize(self):
		szPixels = tuple( self.GetClientSize() )
		self.canvas.SetSize(szPixels)
		szInches = float(szPixels[0])/self.figure.get_dpi() ,  float(szPixels[1])/self.figure.get_dpi()
		self.figure.set_size_inches( szInches[0] , szInches[1] )
		
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




class IdentifySingleStepPanel(wx.Panel):
	def __init__(self,parent,ID=-1,label="",pos=wx.DefaultPosition,size=(100,25)):
		wx.Panel.__init__(self,parent,ID,pos,size,wx.STATIC_BORDER,label)
		self.SetMinSize(size)
		#Create layout:
		self.panelMatplotlib = IdentifyMatplotlibPanel(self, size=(200,300))
		self.checkbox = wx.CheckBox(self, label='Good?', pos=(20, 20))
		self.checkbox.SetValue(True)
		self.rbL = wx.RadioButton(self, -1, 'Left',  (10, 10), style=wx.RB_GROUP)
		self.rbR = wx.RadioButton(self, -1, 'Right', (10, 30))
		self.rbF = wx.RadioButton(self, -1, 'Fore',  (10, 30), style=wx.RB_GROUP)
		self.rbH = wx.RadioButton(self, -1, 'Hind',  (10, 30))
		self.rbL.SetValue(True)
		self.rbF.SetValue(True)
		self.enable(False)
		
		self.checkbox.Bind(wx.EVT_CHECKBOX, self.onCheckbox)
		
		# self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb0.GetId())
		# self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb1.GetId())

		sizerRB0    = wx.BoxSizer(wx.VERTICAL)
		sizerRB0.Add(self.rbL, 1, flag=wx.EXPAND)
		sizerRB0.Add(self.rbR, 1, flag=wx.EXPAND)

		sizerRB1    = wx.BoxSizer(wx.VERTICAL)
		sizerRB1.Add(self.rbF, 1, flag=wx.EXPAND)
		sizerRB1.Add(self.rbH, 1, flag=wx.EXPAND)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.checkbox, 1, flag=wx.EXPAND)
		sizer.Add(sizerRB0, 1, flag=wx.EXPAND)
		sizer.Add(sizerRB1, 1, flag=wx.EXPAND)

		sizer_Main = wx.BoxSizer(wx.VERTICAL)
		sizer_Main.Add(self.panelMatplotlib, 6, flag=wx.EXPAND)
		sizer_Main.Add(sizer, 1)
		
		self.SetSizer(sizer_Main)
		self.Fit()
		# self.Centre()
	
	def cla(self):
		self.panelMatplotlib.cla()
	
	def get_metadata(self):
		good = self.checkbox.GetValue()
		lr   = self.rbR.GetValue()
		fh   = self.rbH.GetValue()
		return good,lr,fh
	
	def enable(self, state=True):
		self.checkbox.Enable(state)
		if state and self.checkbox.GetValue():
			self.rbL.Enable(True)
			self.rbR.Enable(True)
			self.rbH.Enable(True)
			self.rbF.Enable(True)
		else:
			self.rbL.Enable(state)
			self.rbR.Enable(state)
			self.rbH.Enable(state)
			self.rbF.Enable(state)
	
	def onCheckbox(self, event):
		state   = self.checkbox.GetValue()
		self.rbL.Enable(state)
		self.rbR.Enable(state)
		self.rbH.Enable(state)
		self.rbF.Enable(state)
			
	
	
	def plot(self, I, cmax=None):
		self.panelMatplotlib.plot(I, cmax)
		
	def set_metadata_controls(self, good, lr, fh):
		self.checkbox.SetValue(good)
		if lr:
			self.rbR.SetValue(True)
		else:
			self.rbL.SetValue(True)
		
		
		if fh:
			self.rbH.SetValue(True)
		else:
			self.rbF.SetValue(True)
		
		
		if not good:
			self.rbL.Enable(False)
			self.rbR.Enable(False)
			self.rbH.Enable(False)
			self.rbF.Enable(False)



	