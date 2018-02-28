#pressure_module.py

from copy import copy,deepcopy
from math import ceil,floor,cos,sin
from scipy.interpolate import interp1d as scipy_interp1d
import cPickle
import numpy as np
from scipy import ndimage
from matplotlib import pyplot
from matplotlib.mlab import find
import re,tables




def interp1d(y, n=101, dtype=None, kind='linear', axis=-1, copy=True, bounds_error=True, fill_value=np.nan):
	t0       = np.arange(y.shape[0])
	t1       = np.linspace(0, y.shape[0]-1, n)
	f        = scipy_interp1d(t0, y, kind, axis, copy, bounds_error, fill_value)
	y1       = f(t1)
	if dtype != None:
		y1   = np.asarray(y1, dtype=dtype)
	return y1
	
	
#---------------------------------------------
#  PRIVATE FUNCTIONS
#---------------------------------------------


def _centroid(I):
	### get foot coordinates:
	x,y = np.meshgrid(range(I.shape[1]),range(I.shape[0]))
	x,y = x[I>0], y[I>0]
	### compute weighted average:
	w = I[I>0]
	w = w/float(w.sum())   #sum can be an integer
	return np.sum(w*x), np.sum(w*y)



def _centroidXYZ(I):
	### get foot coordinates:
	x,y,z = np.mgrid[0:I.shape[0], 0:I.shape[1], 0:I.shape[2]]
	x,y,z = x[I>0], y[I>0], z[I>0]
	### compute weighted average:
	w = I[I>0]
	w = w/float(w.sum())   #sum can be an integer
	return np.sum(w*x), np.sum(w*y), np.sum(w*z)



def _crop_trial(I0,L):
	uSteps = np.unique(L)[1:]
	nSteps = uSteps.size
	II = []
	for step in range(nSteps):
		I = deepcopy(I0)
		I[L!=uSteps[step]] = 0
		II.append( I )
	return II



def _extract_pixelTS(I):
	return I.flatten().reshape((-1,I.shape[2]))



def _find_heel_strikes(I,L):
	uSteps = np.unique(L)[1:]
	nSteps = uSteps.size
	iSteps = []
	for step in range(nSteps):
		msk = L==uSteps[step]
		for i in range(I.shape[2]):
			if np.any(msk[:,:,i]):
				break
		iSteps.append(i)
	return iSteps



def _find_steps(I0):
	def hereRemoveSmallClusters(L,th=50):
		### remove clusters:
		nLabels = np.unique(L).size-1
		for i in range(nLabels):
			if (L==i+1).sum() < th:
				L[L==i+1]=0
		### renumber:
		uLabels = np.unique(L)
		for i,uLabel in enumerate(uLabels):
			L[L==uLabel] = i
		return L
	def hereClusterDistances(L):
		### extract centroids
		xy = []
		nLabels = np.unique(L).size-1
		for i in range(nLabels):
			xy.append(  _centroidXYZ(np.array(L==i+1,dtype='int'))  )
		### compute distances
		D = np.eye(nLabels)
		D[D==0]=np.nan
		for i in range(nLabels-1):
			for ii in range(i+1,nLabels):
				xy0,xy1 = np.array(xy[i]) , np.array(xy[ii])
				D[i,ii] = ceil(np.sqrt(np.dot(xy0-xy1,xy0-xy1)))
		return D
	def hereRelabelClustersByDistance(labels, D, th=20):
		nLabels = np.unique(labels).size-1
		L = deepcopy(labels)
		#### find close clusters:
		D = D<th
		for i in range(nLabels-1,0,-1):
			ind = find(D[:i,i])
			if len(ind)>0:
				L[labels==(i+1)] = (ind[0]+1)
		return L
	L,nLabels = ndimage.measurements.label(I0)
	L = hereRemoveSmallClusters(L,120)
	D = hereClusterDistances(L)
	L = hereRelabelClustersByDistance(L,D,50)
	return L



def _relabel_steps(L0,iSteps0):
	iSteps  = np.sort(iSteps0)
	indSteps = np.argsort(iSteps0)
	L = deepcopy(L0)
	for ind,step in enumerate(indSteps):
		L[L0==step+1] = ind+1
	return L,iSteps






#---------------------------------------------
#  PUBLIC FUNCTIONS
#---------------------------------------------

def check_DRO(II):
	# ### check an RSscan dynamic roll-off
	# pyplot.clf()
	# for i,I in enumerate(II):
	# 	pyplot.subplot(2,4,i+1);   plot(peakP(I))
	# for i,I in enumerate(II):
	# 	pyplot.subplot(2,4,i+5);   plot(extract_grf(I))
		
	
	# ### plot entire trial:
	# pyplot.axes([0.04,0.09,0.2,0.9])
	# plot(peakP(I))
	# pyplot.title('Entire trial')
	# cmax = ceil(I.max()/10)*10
	# cbh = pyplot.colorbar(  cax=pyplot.axes([0.04,0.09,0.2,0.02])  , orientation='horizontal')
	# pyplot.setp(cbh.ax, xticks=(0,0.5,1), xticklabels=np.linspace(0,cmax,3).astype(int), xlabel=r'Peak pressure $(Ncm^{-2})$'  )

	### plot extracted steps:
	for i,Istep in enumerate(II):
		pyplot.subplot(2,6,i+3);   plot(peakP(Istep))
		pyplot.title('Step %d' %(i+1))
	### plot GRF for each step:
	pyplot.axes([0.35,0.09,0.6,0.4])
	leg_str = []
	for i,Istep in enumerate(II):
		X = extract_grf(Istep)
		pyplot.plot(X)
		leg_str.append('Step %d' %(i+1))
	pyplot.xlabel('Time (frames)')
	pyplot.ylabel('GRF (N)')
	pyplot.legend(leg_str)
	
	


	# ### plot full image:
	# pyplot.axes([0.04,0.09,0.2,0.9])
	# plot(peakP(I))
	# cmax = ceil(I.max()/10)*10
	# cbh = pyplot.colorbar(  cax=pyplot.axes([0.04,0.09,0.2,0.02])  , orientation='horizontal')
	# pyplot.setp(cbh.ax, xticks=(0,0.5,1), xticklabels=np.linspace(0,cmax,3).astype(int), xlabel=r'Peak pressure $(Ncm^{-2})$'  )
	# ### plot GRF:
	# pyplot.axes([0.38,0.25,0.57,0.5])
	# pyplot.plot(extract_grf(I))
	# pyplot.xlabel('Time (frames)')
	# pyplot.ylabel('GRF (N)')


def check_image(I):
	pyplot.clf()
	### plot full image:
	pyplot.axes([0.04,0.09,0.2,0.9])
	plot(peakP(I))
	cmax = ceil(I.max()/10)*10
	cbh = pyplot.colorbar(  cax=pyplot.axes([0.04,0.09,0.2,0.02])  , orientation='horizontal')
	pyplot.setp(cbh.ax, xticks=(0,0.5,1), xticklabels=np.linspace(0,cmax,3).astype(int), xlabel=r'Peak pressure $(Ncm^{-2})$'  )
	### plot GRF:
	pyplot.axes([0.38,0.25,0.57,0.5])
	pyplot.plot(extract_grf(I))
	pyplot.xlabel('Time (frames)')
	pyplot.ylabel('GRF (N)')


def check_registration(I0,I1):
	if I0.ndim==3:
		I0 = I0.max(axis=2)
	if I1.ndim==3:
		I1 = I1.max(axis=2)
	pyplot.imshow(np.ma.masked_array(I0,I0==0), interpolation='nearest', origin='lower')  ### source
	pyplot.contour(I1>0, 1, colors=([0.1]*3,), linewidths=4)   ### template
	pyplot.setp(pyplot.gca(), xticks=[], yticks=[])
	pyplot.axis('image')


def check_trial(I):
	pyplot.clf()
	### plot entire trial:
	pyplot.axes([0.04,0.09,0.2,0.9])
	plot(peakP(I))
	pyplot.title('Entire trial')
	cmax = ceil(I.max()/10)*10
	cbh = pyplot.colorbar(  cax=pyplot.axes([0.04,0.09,0.2,0.02])  , orientation='horizontal')
	pyplot.setp(cbh.ax, xticks=(0,0.5,1), xticklabels=np.linspace(0,cmax,3).astype(int), xlabel=r'Peak pressure $(Ncm^{-2})$'  )
	### plot extracted steps:
	II = extract_steps(I) 
	for i,Istep in enumerate(II):
		pyplot.subplot(2,6,i+3);   plot(peakP(Istep))
		pyplot.title('Step %d' %(i+1))
	### plot GRF for each step:
	pyplot.axes([0.35,0.09,0.6,0.4])
	leg_str = []
	for i,Istep in enumerate(II):
		X = extract_grf(Istep)
		pyplot.plot(X)
		leg_str.append('Step %d' %(i+1))
	pyplot.xlabel('Time (frames)')
	pyplot.ylabel('GRF (N)')
	pyplot.legend(leg_str)
	
	

def contact_durn(I, unit='s', hz=1):
	I = remove_empty_frames(I)
	A = np.zeros(I.shape[:2])
	for i in range(I.shape[0]):
		for ii in range(I.shape[1]):
			A[i,ii] = np.nonzero( (I[i,ii,])>0 )[0].size   #number of nonzero elements
	if unit=='s':
		A = A/float(hz)
	elif unit=='%':
		A = A/float(I.shape[2])
	return A
	
	

def extract_cop(I, interp=False, n=101):
	r = []
	for i in range(I.shape[2]):
		r.append(  _centroid(I[:,:,i])  )
	r = np.array(r)
	if interp:
		r0 = interp1d(r[:,0], n=n)
		r1 = interp1d(r[:,1], n=n)
		r  = np.vstack([r0,r1]).T
	return r


def extract_grf(I):
	X = _extract_pixelTS(I)
	return X.sum(0)*0.5*0.5    #pressure: N/cm2;   pixel size: 5 x 5 mm



def extract_steps(I):
	L        = _find_steps(I)
	iSteps   = _find_heel_strikes(I,L)
	L,iSteps = _relabel_steps(L,iSteps)
	II       = _crop_trial(I,L)
	return II


def find_max_grid(fnames):
	GS = []
	for fname in fnames:
		I = load(fname)
		GS.append( I.shape )
	return tuple(   np.max(GS,axis=0)[:2]   )
	


def load(fname):
	fid = tables.openFile(fname,mode='r')
	I = fid.getNode('/I').read()
	fid.close()
	return I


def load_rois(fname):
	return cPickle.load(open(fname,'rb'))['xy']



def peakP(I):
	return I.max(axis=2)



def plot(I):
	if I.ndim==3:
		print 'Please compute a 2D image before plotting.'
		return
	else:
		pyplot.imshow(np.ma.masked_array(I,I==0), interpolation='nearest', origin='lower')
		pyplot.setp(pyplot.gca(), xticks=[], yticks=[])



def plot_rois(xy):
	XY = np.array(xy)
	pyplot.plot(XY[:,0], XY[:,1], 'wo', markersize=10)





def remove_empty_frames(I):
	X = _extract_pixelTS(I)
	i = np.any(X>0,axis=0)
	return I[:,:,i]


def resize2D(I0,gs1):
	gs0 = I0.shape
	I1  = np.zeros(gs1)
	nRows,nCols = gs1[0]-gs0[0] , gs1[1]-gs0[1]
	xi0,yi0 = np.floor(0.5*nRows) , np.floor(0.5*nCols)
	xi1,yi1 = xi0+gs0[0] , yi0+gs0[1]
	I1[xi0:xi1,yi0:yi1] = I0
	return I1


def resize(I0,gs1):
	gs0 = I0.shape
	nFrames0 = gs0[2]
	I1 =  np.zeros((gs1[0],gs1[1],nFrames0))
	nRows,nCols = gs1[0]-gs0[0] , gs1[1]-gs0[1]
	xi0,yi0 = np.floor(0.5*nRows) , np.floor(0.5*nCols)
	xi1,yi1 = xi0+gs0[0] , yi0+gs0[1]
	I1[xi0:xi1,yi0:yi1,:] = I0
	return I1


def resize_all(fnames, pad=0):
	print 'Finding maximum grid...'
	gs = find_max_grid(fnames)
	gs = [gs[0]+2*pad, gs[1]+2*pad]
	print 'Max grid: = [%d %d]' %tuple(gs)
	print 'Resizing and saving images...'
	for fname in fnames:
		I = load(fname)
		I = resize(I,gs)
		save(fname,I)
	print 'Done.'


def save(fname,I):
	fid = tables.openFile(fname,mode='w')
	try:
		atom = tables.UInt16Atom()
		filter = tables.Filters(complevel=9, complib='zlib')
		A = fid.createCArray(fid.root, 'I', atom, I.shape, filters=filter)
		A[:] = I
		fid.close()
	except:
		print 'Error saving file.'
		fid.close()

def save_rois(fname,xy):
	cPickle.dump(  {'xy':xy}, open(fname,'wb'))


def select_rois(I, n=5):
	plot(I)
	return pyplot.ginput(n=n, timeout=-1, show_clicks=True)


def subsample(I, xy):
	if type(I)==list:
		z = [subsample(II,xy) for II in I]
	if type(I)==np.ndarray:
		z = []
		for i in range(len(xy)):
			x,y = xy[i][1], xy[i][0]
			x0,y0 = floor(x), floor(y)
			x1,y1 = x0+1, y0+1
			z.append(   (x1-x)*(y1-y)*I[x0,y0] + (x1-x)*(y-y0)*I[x0,y1] + (x-x0)*(y1-y)*I[x1,y0] + (x-x0)*(y-y0)*I[x1,y1]  )
	return np.array(z)
			# I[x0,y0]*(x1-x)*(y1-y)  + I[x1,y0]*(x-x0)*(y1-y) + I[x0,y1]*(x1-x)*(y-y0) + I[x1,y1]*(x-x0)*(y-y0)
			

def tight(I):
	B  = I>0
	if I.ndim==2:
		ix = B.any(1);   ix0,ix1 = min(find(ix)) , max(find(ix))+1
		iy = B.any(0);   iy0,iy1 = min(find(iy)) , max(find(iy))+1
		return I[ix0:ix1,iy0:iy1]
	elif I.ndim==3:
		ix = B.max(2).any(1);   ix0,ix1 = min(find(ix)) , max(find(ix))+1
		iy = B.max(2).any(0);   iy0,iy1 = min(find(iy)) , max(find(iy))+1
		iz = B.max(0).any(0);   iz0,iz1 = min(find(iz)) , max(find(iz))+1
		return I[ix0:ix1,iy0:iy1,iz0:iz1]



def time2first(I, unit='s', hz=1):
	I = remove_empty_frames(I)
	A = np.argmax(I>0, axis=2)
	if unit=='s':
		A = A/float(hz)
	elif unit=='%':
		A = A/float(I.shape[2])
	return A


def time2peak(I, unit='s', hz=1):
	I = remove_empty_frames(I)
	A = np.argmax(I, axis=2)
	if unit=='s':
		A = A/float(hz)
	elif unit=='%':
		A = A/float(I.shape[2])
	return A



def transformXYRS(I,q):  #q is a four-tuple: (x,y,theta,scale)
	def shiftFn(x,c0,q0):  #( original pixel coordinates , image centroid , rigid parameters )
		c = (c0[1],c0[0])
		q = (-q0[1],-q0[0],q0[2])
		s = 1.0/q0[3]
		cq3,sq3 = cos(q[2]) , sin(q[2])
		xp0 = c[0] + q[0]*cq3 - q[1]*sq3      +s*x[0]*cq3 -x[1]*sq3 -s*c[0]*cq3 +c[1]*sq3
		xp1 = c[1] + q[0]*sq3 + q[1]*cq3      +x[0]*sq3 +s*x[1]*cq3 -c[0]*sq3 -s*c[1]*cq3
		return ( xp0, xp1, x[2] )

	c = (0.5*I.shape[1],0.5*I.shape[0])
	I = ndimage.geometric_transform(I, shiftFn, order=1, extra_arguments=(c,q))
	return I

def transform2D(I, q):  #q is a four-tuple: (x,y,theta,scale)
	def shiftFn(x, c0, q0):  #( original pixel coordinates , image centroid , rigid parameters )
		c = c0[1],c0[0]
		q = -q0[1], -q0[0], q0[2]
		s = 1.0/q0[3]
		cq3,sq3 = cos(q[2]) , sin(q[2])
		xp0 = c[0] + q[0]*cq3 - q[1]*sq3      +s*x[0]*cq3 -x[1]*sq3 -s*c[0]*cq3 +c[1]*sq3
		xp1 = c[1] + q[0]*sq3 + q[1]*cq3      +x[0]*sq3 +s*x[1]*cq3 -c[0]*sq3 -s*c[1]*cq3
		return xp0, xp1
	c = 0.5*I.shape[1], 0.5*I.shape[0]
	I = ndimage.geometric_transform(I, shiftFn, order=1, extra_arguments=(c,q))
	return I


	


