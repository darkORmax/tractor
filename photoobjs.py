import logging
from astrometry.util.fits import *
from astrometry.util.sdss_radec_to_rcf import *

#### From sequels.py ####

class PrimaryArea(object):
    def __init__(self, fn='field_primary.fits'):
        print 'Reading', fn, '...'
        F = fits_table(fn)
        self.fieldAreas = dict([((int(rr),int(r),int(c),int(f)),a) for rr,r,c,f,a
                                in zip(F.rerun, F.run, F.camcol, F.field, F.primaryarea)])
        del F

    def get(self, rr, run, camcol, field):
        pa = self.fieldAreas.get((int(rr),int(run),int(camcol),int(field)), None)
        return pa


photoobjdir = 'photoObjs-new'

def get_photoobj_filename(rr, run, camcol, field):
    fn = os.path.join(photoobjdir, rr, '%i'%run, '%i'%camcol,
                      'photoObj-%06i-%i-%04i.fits' % (run, camcol, field))
    return fn

def read_photoobjs(sdss, wcs, margin, cols=None, pa=None, wfn='window_flist.fits'):
    '''
    Read photoObjs that are inside the given 'wcs', plus 'margin' in degrees.

    If 'pa' is not None, assume it is a PrimaryArea object.
    '''
    log = logging.getLogger('read_photoobjs')

    #wfn = os.path.join(resolvedir, 'window_flist.fits')

    ra,dec = wcs.radec_center()
    rad = wcs.radius()
    rad += np.hypot(13., 9.) / 2 / 60.
    # a little extra margin
    rad += margin

    print 'Searching for run,camcol,fields with radius', rad, 'deg'
    RCF = radec_to_sdss_rcf(ra, dec, radius=rad*60., tablefn=wfn)
    log.debug('Found %i fields possibly in range' % len(RCF))

    pixmargin = margin * 3600. / wcs.pixel_scale()
    W,H = wcs.get_width(), wcs.get_height()
    
    TT = []
    for run,camcol,field,r,d in RCF:
        log.debug('RCF %i/%i/%i' % (run, camcol, field))
        rr = sdss.get_rerun(run, field=field)
        if rr in [None, '157']:
            log.debug('Rerun 157')
            continue

        if pa is not None:
            if pa.get(rr, run, camcol, field) == 0:
                log.debug('RCF %i/%i/%i has primaryArea = 0; skipping' %
                          (run,camcol,field))
                continue

        fn = get_photoobj_filename(rr, run, camcol, field)

        T = fits_table(fn, columns=cols)
        if T is None:
            log.debug('read 0 from %s' % fn)
            continue
        log.debug('read %i from %s' % (len(T), fn))

        # while we're reading it, record its length for later...
        #get_photoobj_length(rr, run, camcol, field)

        ok,x,y = wcs.radec2pixelxy(T.ra, T.dec)
        x -= 1
        y -= 1
        T.cut((x > -pixmargin) * (x < (W + pixmargin)) *
              (y > -pixmargin) * (y < (H + pixmargin)) *
              (T.resolve_status & 256) > 0)
        log.debug('cut to %i within target area and PRIMARY.' % len(T))
        if len(T) == 0:
            continue

        TT.append(T)
    if not len(TT):
        return None
    T = merge_tables(TT)
    return T
