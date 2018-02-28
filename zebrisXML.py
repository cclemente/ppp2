
from xml.etree.ElementTree import ElementTree
import numpy as np

__version__ = '0.0.0001  (2014.06.26)'




class ZebrisXMLImporter(object):
	def __init__(self, fname):
		self.events     = None
		self.fname      = fname
		self.hz         = None
		self.root       = None
		self.movements  = None
		self.nEvents    = None
		self.nMovements = None
		self.tree       = ElementTree()
		self.xmlns      = '{http://www.zebris.de/measurements}'
		self.xoffset    = 44 + 12 - 1  #(gap between plates)
		self._init()
		
		
	def _init(self):
		self.tree.parse(self.fname)
		self.root       = self.tree.getroot()
		self.movements  = self.find(self.root, 'movements').getchildren()
		self.events     = [self.findall(movement, 'clips/clip/data/event')  for movement in self.movements]
		self.nEvents    = [len(events) for events in self.events]
		### eliminate zero-event movements:
		good_movement   = [n>0 for n in self.nEvents]
		self.movements  = [m for m,g in zip(self.events,good_movement) if g]
		self.events     = [e for e,g in zip(self.events,good_movement) if g]
		self.nMovements = len(self.movements)
		self.nEvents    = [len(events) for events in self.events]
		if self.nMovements>0:
			self.hz     = int( self.find(self.events[0][0], 'rollover/frequency').text  )


	def _xmlns_searchstring(self, base, leaf):
		s = ''
		for ss in leaf.split('/'):
			s += self.xmlns + ss + '/'
		return s[:-1]
	def find(self, base, leaf):
		s = self._xmlns_searchstring(base, leaf)
		return base.find(s)
	def findall(self, base, leaf):
		s = self._xmlns_searchstring(base, leaf)
		return base.findall(s)
		
		
	def get_event_cellsize(self, event):
		x       = float( self.find(event, 'cell_size/x').text )
		y       = float( self.find(event, 'cell_size/y').text )
		return x,y		
	def get_event_origin(self, event):
		x       = int( self.find(event, 'max/cell_begin/x').text )
		y       = int( self.find(event, 'max/cell_begin/y').text )
		return x,y
	def get_event_rectangle(self, event):
		x,y     = self.get_event_origin(event)
		nR,nC   = self.get_event_shape(event)
		return x,y,nC,nR
	def get_event_shape(self, event):
		nCols   = int( self.find(event, 'max/cell_count/x').text )
		nRows   = int( self.find(event, 'max/cell_count/y').text )
		return nRows,nCols
	def get_event_times(self, event):
		t0      = float( self.find(event, 'begin').text )
		t1      = float( self.find(event, 'end').text )
		return t0,t1
	def get_event_times_as_ind(self, event):
		t0,t1   = self.get_event_times(event)
		return int(t0*self.hz), int(t1*self.hz)
		
	
	
	def get_gridsize_plate(self):
		nCols   = int( self.find(self.root, 'cell_count/x').text )
		nRows   = int( self.find(self.root, 'cell_count/y').text )
		return nRows, nCols
		
	
	def get_movement_direction(self, movement):
		return self.find(movement, 'type').text
	def get_movement_directions(self):
		return [self.find(movement, 'type').text  for movement in self.movements]
	
	
	
	def get_quant_origin(self, quant):
		x       = int( self.find(quant, 'cell_begin/x').text )
		y       = int( self.find(quant, 'cell_begin/y').text )
		return x,y
	def get_quant_rectangle(self, quant):
		x,y     = self.get_quant_origin(quant)
		nR,nC   = self.get_quant_shape(quant)
		return x,y,nC,nR
	def get_quant_shape(self, quant):
		nCols   = int( self.find(quant, 'cell_count/x').text )
		nRows   = int( self.find(quant, 'cell_count/y').text )
		return nRows,nCols
	
	
	
	def get_rollover_shape(self, rollover):
		nCols   = int( self.find(rollover, 'cell_count/x').text )
		nRows   = int( self.find(rollover, 'cell_count/y').text )
		nFrames = int( self.find(rollover, 'count').text )
		return nRows,nCols,nFrames
	
	
	def is_edge_event(self, event):
		ny,nx        = self.get_gridsize_plate()
		x,y,w,h      = self.get_event_rectangle(event)
		isouteredge  = (x==1) or (y==1) or ((x+w)>=nx) or ((y+h)>=ny)
		ismiddleedge = False   #to implement later
		isedge       = isouteredge or ismiddleedge
		return isedge


	def read_cells(self, cells):
		I  = [s.strip().split(' ')   for s in cells.text.split('\n')[1:-1]]
		return np.flipud( np.asarray(10*np.array(I, dtype=float), dtype=np.uint16)  )

	
	
	def read_grf(self, event, discard_edge_steps=False):
		if discard_edge_steps and self.is_edge_event(event):
			F  = None
		else:
			sx,sy    = self.get_event_cellsize(event)
			rollover = self.find(event, 'rollover')
			nFrames  = self.get_rollover_shape(rollover)[2]
			F        = np.zeros(nFrames)
			data     = self.find(rollover, 'data')
			for i,quant in enumerate(data.getchildren()):
				cells = self.find(quant, 'cells')
				F[i]  = self.read_cells(cells).sum()
			F *= 0.001 * sx * sy
		return F


	def read_max(self, event, discard_edge_steps=False):
		if discard_edge_steps and self.is_edge_event(event):
			I  = None
		else:
			I  = self.read_cells( self.find(event, 'max/cells') )
		return I

	def read_rollover(self, event, discard_edge_steps=False):
		if discard_edge_steps and self.is_edge_event(event):
			I  = None
		else:
			rollover = self.find(event, 'rollover')
			nRows,nCols,nFrames = self.get_rollover_shape(rollover)
			I     = np.zeros((nRows,nCols,nFrames), dtype=np.uint16)
			data  = self.find(rollover, 'data')
			for i,quant in enumerate(data.getchildren()):
				x0,y0,nx,ny = self.get_quant_rectangle(quant)
				cells       = self.find(quant, 'cells')
				I[y0:y0+ny,x0:x0+nx,i] = self.read_cells(cells)
		return I




def import_steps_grf(fname, discard_edge_steps=False):
	z   = ZebrisXMLImporter(fname)
	FF  = [[z.read_grf(event, discard_edge_steps)  for event in events]  for events in z.events]
	return FF

def import_steps_max(fname, discard_edge_steps=False):
	z   = ZebrisXMLImporter(fname)
	II  = [[z.read_max(event, discard_edge_steps)  for event in events]  for events in z.events]
	return II

def import_steps_rollover(fname, discard_edge_steps=False):
	z   = ZebrisXMLImporter(fname)
	II  = [[z.read_rollover(event, discard_edge_steps)  for event in events]  for events in z.events]
	return II


