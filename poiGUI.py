
import wx
import numpy as np
from poiGUI_panels import POIPanel
from poiGUI_navigation import POINavigationControls


class POIFrame(wx.Frame):
	def __init__(self, parent, id, title, metadata=None):
		wx.Frame.__init__(self, parent, id, title)
		self.POI             = metadata.load_pois()
		self.poi             = self.POI[0]
		self.selected        = [None]*4
		self.metadata        = metadata
		# self.nRollovers      = None
		# self.panels          = None
		# self.rollovers       = None
		# self.stepnums        = None
		# self.subj            = None
		# self.xmlfilenames    = None
		sizer                = self._create_panels()
		self._create_statusbar()
		self.SetSizer(sizer)
		self.Fit()
		self.Centre()
		self.set_subject(0)
		

	def _create_panels(self):
		### create steps panels:
		sizer0             = wx.BoxSizer(wx.HORIZONTAL)
		# self.panels        = [MatplotlibPanel(self, size=(200,340), panelnum=i)  for i in range(4)]
		self.panels        = [POIPanel(self, size=(200,340), panelnum=i)  for i in range(4)]
		[sizer0.Add(panel, 1, flag=wx.EXPAND) for panel in self.panels]
		panel_nav  = POINavigationControls(self, size=(200,50))
		### add to a sizer:
		sizer      = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(sizer0, 8, flag=wx.EXPAND)
		sizer.Add(panel_nav, 1, flag=wx.EXPAND)
		return sizer
		
	def _create_statusbar(self):
		self.statusbar = self.CreateStatusBar(style=wx.BORDER_DOUBLE)
		self.statusbar.SetFieldsCount(3)
		self.statusbar.SetStatusWidths([-5,-1,-3])

	def _find_closest_poi(self, xy, panelnum):
		d   = []
		x,y = xy
		for poi in self.poi[panelnum]:
			x0,y0 = poi
			d.append(  (x-x0)**2 + (y-y0)**2  )
		return np.argmin(d)
	
	def back(self):
		self.statusbar.SetStatusText('(Loading data...)', 2)
		subj  = self.subj
		if subj - 1 < 0:
			subj = self.metadata.nSubj - 1
		else:
			subj -= 1
		self.set_subject(subj)

	
	def get_current_pois(self, panelnum):
		return np.array([line.get_data() in self.panels[panelnum].ax.lines]).squeeze()


	def forward(self):
		self.statusbar.SetStatusText('(Loading data...)', 2)
		subj  = self.subj
		if subj + 1 == self.metadata.nSubj:
			subj = 0
		else:
			subj += 1
		self.set_subject(subj)
		
	def poi_add(self, xy, panelnum):
		panel = self.panels[panelnum]
		panel.plot_poi(xy)
		panel.canvas.draw()
		if self.poi[panelnum]==None:
			self.poi[panelnum] = [xy]
		else:
			self.poi[panelnum].append(xy)
		self.selected[panelnum] = len(self.poi[panelnum])
		self.panels[panelnum].highlight_poi( self.selected[panelnum]   )

	def poi_delete(self, xy, panelnum):
		if self.poi[panelnum]==None:
			pass
		else:
			ind   = self._find_closest_poi(xy, panelnum)
			self.poi[panelnum].pop(ind)
			if len(self.poi[panelnum])==0:
				self.poi[panelnum] = None
				self.selected[panelnum] = None
			self.panels[panelnum].replot_pois(self.poi[panelnum])
	
	def poi_select(self, xy, panelnum):
		if self.poi[panelnum]==None:
			pass
		else:
			ind   = self._find_closest_poi(xy, panelnum)
			self.panels[panelnum].highlight_poi(ind)

	
	def quit(self):
		# result = wx.MessageBox('Previously specified POIs will be overwritten. OK to proceed?', 'Confirm overwrite', wx.OK | wx.CANCEL)
		# if result==wx.OK:
		# 	self.metadata.save_template_choices(self.CHOICES)
		self.Destroy()
		

	def set_subject(self, subj):
		self.subj = subj
		II        = self.metadata.load_means(self.subj, stacked=False)
		[panel.plot( np.asarray(I, dtype=float) )  for panel,I in zip(self.panels,II)]
		# self.set_statusbar_text()
		
	
	def set_statusbar_text(self):
		self.statusbar.SetStatusText('Subj %d of %d'%(self.subj+1,self.metadata.nSubj), 1)
		self.statusbar.SetStatusText(self.metadata.USUBJ[self.subj], 2)




class MyApp(wx.App):
	def OnInit(self):
		import pressure_database as DB;  reload(DB)
		# dir0     = '/Volumes/DataProc/projectsExternal/uQueensland/test2/'
		dir0     = '/Users/todd/Desktop/test2'
		metadata = DB.load_metadata(dir0)
		subj = 0
		frame = POIFrame(None, -1, 'Points of Interest (POIs)', metadata=metadata)
		frame.Show(True)
		self.SetTopWindow(frame)
		return True



# #run app:
# app = MyApp(redirect=False)
# app.MainLoop()

