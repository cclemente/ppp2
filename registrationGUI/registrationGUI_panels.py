
import wx
import numpy as np
from matplotlib import pyplot
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure
import pressure_module as PM



class RegistrationPanel(wx.Panel):
	def __init__(self, parent, ID=-1, label="", pos=wx.DefaultPosition, size=(100,25)):
		#(0) Initialize panel:
		wx.Panel.__init__(self, parent, ID, pos, size, style=wx.STATIC_BORDER|wx.WANTS_CHARS, name=label)
		self.SetMinSize(size)
		self.parent = parent
		self.q      = [0, 0, 0, 1]
		self.th     = 5
		#(1) Create Matplotlib figure:
		self.figure = Figure(facecolor='0.8')
		self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
		self._resize()
		self._create_axes()
		self.canvas.Bind(wx.EVT_KEY_DOWN, self.callback_key)
		self.canvas.Bind(wx.EVT_CHAR_HOOK, self.callback_key)


	def callback_key(self, event):
		keycode = event.GetKeyCode()
		
		#(0) Escape to exit:
		if keycode == wx.WXK_ESCAPE:
			ans  = wx.MessageBox('Are you sure you want to quit?', '', wx.YES_NO | wx.CENTRE | wx.NO_DEFAULT, self)
			if ans == wx.YES:
				self.parent.quit()
		#(1) Enter to finish:
		if keycode == wx.WXK_RETURN:
			self.parent.forward()
		#(2) Update transformation parameters:
		amp = 0.1 + (event.ControlDown()*(1-0.1)) + (event.ShiftDown()*(5-0.1))
		if keycode == wx.WXK_UP:  	self.q[1] += amp
		if keycode == wx.WXK_DOWN:	self.q[1] -= amp
		if keycode == wx.WXK_LEFT:	self.q[0] -= amp
		if keycode == wx.WXK_RIGHT:	self.q[0] += amp

		if keycode == 328:              self.q[0] -= amp
		if keycode == 330:              self.q[0] += amp
                if keycode == 326:              self.q[1] -= amp
		if keycode == 332:              self.q[1] += amp

		if keycode in [91,123]:		self.q[2] += 0.2*amp   # '['
		if keycode in [93,125]:		self.q[2] -= 0.2*amp   # ']'
		self.transform()

	def _create_axes(self):
		self.ax = self.figure.add_axes((0,0,1,1), axisbg=[0.5]*3)
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
	
	def plot(self):  #initial plot (after navigating to a new image)
		I       = PM.transform2D(self.I, self.q)
		self.IT = I.copy()
		self.plot_source()
		# I[I==0] = np.nan
		# self.ax.imshow(I, interpolation='nearest', origin='lower', vmin=0, vmax=self.cmax)
		pyplot.setp(self.ax, xticks=[], yticks=[])
		self.ax.set_axis_bgcolor([0.05]*3)
		self.ax.axis('image')
		self.canvas.draw()
	
	def plot_source(self):   #plot source (thresholded according to slider value)
		if self.ax.images:
			self.ax.images.pop(0)
		I = self.IT.copy()
		I[I<=self.th] = np.nan
		self.ax.imshow(I, interpolation='nearest', origin='lower', vmin=0, vmax=self.cmax)
	
	def plot_template(self, I0, th=0):  #plot template (thresholded according to slider value)
		self.th  = th
		if self.ax.collections:
			self.ax.collections.pop(0)
		self.ax.contour(I0>th, 1, colors="0.5", linewidths=3)
		self.plot_source()
		self.canvas.draw()
	
	def set_Iq(self, I, q):
		self.I    = I.copy()
		self.q    = q
		self.cmax = 0.95*I.max()

	def transform(self):   #transform the source
		I       = PM.transform2D(self.I, self.q)
		self.IT = I.copy()
		self.plot_source()
		self.canvas.draw()
		




	