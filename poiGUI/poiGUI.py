
import os,wx
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
		self.subj            = 0
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
		buttonR    = wx.Button(self, -1, 'Reset', (200, 200))
		buttonX    = wx.Button(self, -1, 'Export', (200, 200))
		panel_nav  = POINavigationControls(self, size=(200,50))
		### bind:
		buttonR.Bind(wx.EVT_BUTTON, self.OnButtonReset)
		buttonX.Bind(wx.EVT_BUTTON, self.OnButtonExport)
		sizerH     = wx.BoxSizer(wx.HORIZONTAL)
		sizerH.Add(buttonR, 1, flag=wx.CENTER)
		sizerH.Add(buttonX, 1, flag=wx.CENTER)
		### layout:
		sizer      = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(sizer0, 8, flag=wx.EXPAND)
		sizer.Add(sizerH, 1, flag=wx.CENTER)
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
		self.POI[self.subj] = self.poi
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
		self.POI[self.subj] = self.poi
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
		self.selected[panelnum] = len(self.poi[panelnum])-1
		self.panels[panelnum].highlight_poi( self.selected[panelnum]   )
		self.panels[panelnum].set_xy(xy)

	def poi_delete(self, xy, panelnum):
		if self.poi[panelnum]==None:
			pass
		else:
			ind   = self._find_closest_poi(xy, panelnum)
			panel = self.panels[panelnum]
			self.poi[panelnum].pop(ind)
			if len(self.poi[panelnum])==0:
				self.poi[panelnum] = None
				self.selected[panelnum] = None
				panel.set_xy(None)
			else:
				if ind==self.selected[panelnum]:
					self.selected[panelnum] = 0
				elif self.selected[panelnum] > ind:
					self.selected[panelnum] -= 1
				# else:
				# 	self.selected[panelnum] -= 1
				panel.set_xy(xy)
			panel.replot_pois(self.poi[panelnum])
			panel.highlight_poi( self.selected[panelnum]   )
	
	def poi_move_selected(self, panelnum, x=None, y=None):
		ind   = self.selected[panelnum]
		xy    = list(self.poi[panelnum][ind])
		if x!=None:
			xy[0] = x
		if y!=None:
			xy[1] = y
		self.poi[panelnum][ind]  = xy
		panel = self.panels[panelnum]
		panel.replot_pois(self.poi[panelnum])
		panel.highlight_poi( self.selected[panelnum]   )
	
	def poi_select(self, xy, panelnum):
		if self.poi[panelnum]==None:
			pass
		else:
			ind   = self._find_closest_poi(xy, panelnum)
			self.panels[panelnum].highlight_poi(ind)
			self.panels[panelnum].set_xy(  self.poi[panelnum][ind]  )
			self.selected[panelnum] = ind
			

	
	def quit(self):
		result = wx.MessageBox('Previously specified POIs will be overwritten. OK to proceed?', 'Confirm overwrite', wx.OK | wx.CANCEL)
		if result==wx.OK:
			self.metadata.save_pois(self.POI)
		self.Destroy()
		

	def set_subject(self, subj):
		self.subj = subj
		self.poi  = self.POI[subj]
		II        = self.metadata.load_means(subj, stacked=False)
		[panel.cla()  for panel in self.panels]
		[panel.plot( np.asarray(I, dtype=float) )  for panel,I in zip(self.panels,II)]
		for i,(panel,poi) in enumerate(zip(self.panels,self.poi)):
			panel.replot_pois(poi)
			if poi==None:
				self.selected[i] = None
				panel.set_xy(None)
			else:
				self.selected[i] = 0
				panel.highlight_poi(0)
				panel.set_xy( poi[0] )
		self.set_statusbar_text()
		
	
	def set_statusbar_text(self):
		self.statusbar.SetStatusText('Subj %d of %d'%(self.subj+1,self.metadata.nSubj), 1)
		self.statusbar.SetStatusText(self.metadata.USUBJ[self.subj], 2)
		
		
	def OnButtonExport(self, event):
		# fname         = os.path.join('/Users/todd/Desktop/poi_export.xls')
		dialog = wx.FileDialog(self, 'Select a destination...', '.', defaultFile='poi_export.xls', style=wx.FD_SAVE)
		fname  = None
		if dialog.ShowModal() == wx.ID_OK:
			fname = dialog.GetPath()
		dialog.Destroy()
		if fname!=None:
			 self.metadata.save_poi_extracted(fname, self.POI)
		
	def OnButtonReset(self, event):
		result = wx.MessageBox('WARNING:  All POI data will be deleted.\nOK to continue?\n\nNote: the POIs will be deleted from this screen but not from disk. To rese the POIs stored on disk, select "OK", then select "Quit" and "OK" to overwrite the existing POIs.', 'Confirm POI reset', wx.OK | wx.CANCEL)
		if result==wx.OK:
			self.POI = [[None]*4  for i in range(self.metadata.nSubj)]
			self.set_subject(self.subj)



# class MyApp(wx.App):
# 	def OnInit(self):
# 		import pressure_database as DB;  reload(DB)
# 		# dir0     = '/Volumes/DataProc/projectsExternal/uQueensland/test2/'
# 		dir0     = '/Users/todd/Desktop/test2'
# 		metadata = DB.load_metadata(dir0)
# 		subj = 0
# 		frame = POIFrame(None, -1, 'Points of Interest (POIs)', metadata=metadata)
# 		frame.Show(True)
# 		self.SetTopWindow(frame)
# 		return True
#
#
#
# #run app:
# app = MyApp(redirect=False)
# app.MainLoop()

