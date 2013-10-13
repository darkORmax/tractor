#! /usr/bin/env python

import matplotlib
matplotlib.use('Agg')
import numpy as np
import pylab as plt
import os
import sys
import fitsio

from astrometry.util.file import *
from astrometry.util.fits import *
from astrometry.util.multiproc import *
from astrometry.util.plotutils import *
from astrometry.util.miscutils import *
from astrometry.util.util import *
from astrometry.blind.plotstuff import *

if __name__ == '__main__':
    #    W,H = 4000,2000
    W,H = 400,200
    plot = Plotstuff(size=(W,H), outformat='png')
    plot.wcs = anwcs_create_allsky_hammer_aitoff(180., 0., W, H)
    out = plot.outline
    #out.stepsize = 508
    out.stepsize = 2000
    out.fill = 1
    
    #log_init(3)
    
    #im = np.zeros((H,W,4), np.uint8)

    wcs = Tan()
    out.wcs = anwcs_new_tan(wcs)
    print 'out.wcs', out.wcs
    wcs = anwcs_get_sip(out.wcs)
    print 'wcs', wcs
    wcs = wcs.wcstan
    print 'wcs', wcs
    
    ps = PlotSequence('cov')
    #for nbands in [4,3,2]:
    for nbands in [4]:
        bb = [1,2,3,4][:nbands]
        #for band in bb:
        band = 1
        for fn in ['4band.fits', '4band2.fits']:
            count = np.zeros((H,W), np.int16)
            #fn = 'wise-frames/WISE-l1b-metadata-%iband.fits' % nbands
            cols = [('w%i'%band)+c for c in
                    ['crval1','crval2','crpix1','crpix2',
                     'cd1_1','cd1_2','cd2_1','cd2_2', 'naxis1','naxis2']]

            #cols = [('w%i'%band)+c for c in
            #        ['ra1','dec1','ra2','dec2','ra3','dec3','ra4','dec4']]

            print 'Reading', fn
            T = fits_table(fn, columns=cols)
            print 'Read', len(T), 'from', fn
            #wcs = Tan()

            #T = T[1:2]

            arrs = [T.get(c).astype(float) for c in cols]
            #r1,d1,r2,d2,r3,d3,r4,d4 = arrs

            plot.clear()
            plot.color = 'white'
            #plot.alpha = 1./255.
            plot.alpha = 1.
            plot.op = CAIRO_OPERATOR_ADD

            N = len(T)
            for i in xrange(N):
                print
                print 'WCS', i
                wcs.set(*[a[i] for a in arrs])
                #out.wcs = anwcs_new_tan(wcs)
                plot.plot('outline')

                # plot.move_to_radec(r1[i], d1[i])
                # plot.line_to_radec(r2[i], d2[i])
                # plot.line_to_radec(r3[i], d3[i])
                # plot.line_to_radec(r4[i], d4[i])
                # plot.close_path()
                # plot.fill()

                #print '.',

                if i and i % 10000 == 0 or i == N-1:

                    fn = ps.getnext()
                    plot.write(fn)
                    
                    print 'exposure', i, 'of', N
                    im = plot.get_image_as_numpy()
                    #plot.get_image_as_numpy(out=im)
                    print 'im:', im.shape
                    print 'max:', im[:,:,0].max()
                    #im = im[:,:,0]
                    count += im[:,:,0]
                    del im
                    print 'total max:', count.max()
                    plot.clear()
                    
            ofn = 'cov-n%i-b%i.fits' % (nbands, band)
            fitsio.write(ofn, count, clobber=True)
            print 'Wrote', ofn

            plt.clf()
            plt.imshow(count, interpolation='nearest', origin='lower',
                       vmin=0, vmax=1, cmap='gray')
            ps.savefig()
            
            #sys.exit(0)
