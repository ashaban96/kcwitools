""" Image generation and manipulation routines"""
from __future__ import print_function, absolute_import, division, unicode_literals

###trim off the crap parts of the KCWI cube
def kcwi_cube_trim(infil):
    wave, flux, hdr = open_kcwi_cube(infil)
    trimflux = flux[:, 18:81, 6:28]  # note that python reads arrays weird.  Trim *down in y* then x.

    a, b = infil.split(".fits")
    outfil = a + '_trimmed.fits'

    hdu_out = fits.PrimaryHDU(trimflux, header=hdr)
    hdu_out.writeto(outfil, overwrite=True)


###trim off crap parts of larger kcwi cube
def kcwi_cube_trim_large(infil):
    wave, flux, hdr = open_kcwi_cube(infil)
    trimflux = flux[:, 15:81, 2:26]  # note that python reads arrays weird.  Trim *down in y* then x.

    a, b = infil.split(".fits")
    outfil = a + '_trimmed.fits'

    hdu_out = fits.PrimaryHDU(trimflux, header=hdr)
    hdu_out.writeto(outfil, overwrite=True)


def build_narrowband(zabs, infil, del_wave=2.0, ion='HI', restwave=1215.6701):
    if (ion == 'HI'):
        restwave = 1215.6701

    wave, flux, hdr = open_kcwi_cube(infil)
    # Work out the slices for the on-band image:
    slices = np.where((wave >= (1.0 + zabs) * (restwave - del_wave)) &
                      (wave <= (1.0 + zabs) * (restwave + del_wave)))
    slices = slices[0]

    # define windows on either side of the slice (watch out for a,b and <= vs <)
    offimage_width = 2. * del_wave

    slice_low = np.where((wave >= (1.0 + zabs) * (restwave - del_wave - offimage_width)) &
                         (wave < (1.0 + zabs) * (restwave - del_wave)))[0]
    slice_high = np.where((wave >= (1.0 + zabs) * (restwave + del_wave)) &
                          (wave < (1.0 + zabs) * (restwave + del_wave + offimage_width)))[0]

    # Make the on-band and two off-band images
    nbimage = np.average(flux[slices, :, :], 0)
    high = np.average(flux[slice_high, :, :], 0)
    low = np.average(flux[slice_low, :, :], 0)

    # Average the two off-band images and subtract.
    offimage = (low + high) / 2.0
    # nbimage = nbimage - offimage

def cube_skysub(fil, skyy1, skyy2, skyx1, skyx2, outfil):
    wave, flux, hdr = open_kcwi_cube(fil)
    wavedim, ydim, xdim = flux.shape
    sky = np.zeros(wavedim)

    for i in range(wavedim):
        sky[i] = np.median(flux[i, skyy1:skyy2, skyx1:skyx2])

    # Now Sky subtract the whole cube
    fluxmsky = np.zeros((wavedim, ydim, xdim))
    for i in range(wavedim):
        fluxmsky[i, :, :] = flux[i, :, :] - sky[i]

    hdu_out = fits.PrimaryHDU(fluxmsky, header=hdr)
    hdu_out.writeto(outfil, overwrite=True)


def var_skysub(varfil, skyy1, skyy2, skyx1, skyx2, outfil):
    wave, var, hdr = open_kcwi_cube(varfil)
    wavedim, ydim, xdim = var.shape
    sky = np.zeros(wavedim)

    for i in range(wavedim):
        sky[i] = np.median(var[i, skyy1:skyy2, skyx1:skyx2])

    # Now Sky subtract the whole cube
    varwsky = np.zeros((wavedim, ydim, xdim))
    for i in range(wavedim):
        varwsky[i, :, :] = var[i, :, :] + sky[i]

    hdu_out = fits.PrimaryHDU(varwsky, header=hdr)
    hdu_out.writeto(outfil, overwrite=True)

