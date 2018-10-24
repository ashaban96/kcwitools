""" utility routines"""
from __future__ import print_function, absolute_import, division, unicode_literals
import numpy as np

from astropy import units


def build_wave(hdu_hdr, air2vac=True):
    """

    Args:
        hdu_hdr:

    Returns:
        wave: ndarray

    """
    crval3 = hdu_hdr['CRVAL3']
    crpix3 = hdu_hdr['CRPIX3']
    cd3_3 = hdu_hdr['CD3_3']
    wavedim = hdu_hdr['NAXIS3']
    # Do it
    wave = crval3 + (crpix3 + np.arange(0, wavedim, 1.0)) * cd3_3
    # Air2vac?
    if air2vac:
        wave = airtovac(wave)
    # Return
    return wave

def set_radec(hdu_hdr, ra, dec, x, y):
    """
    Modify the Header to force RA/DEC value at a given x,y position

    Args:
        hdu_hdr: Header
        ra: float (deg)
        dec: float (deg)
        x: float
          x pixel position in the image
        y: float
          y pixel position in the image

    Returns:
        new_hdr: Header

    """
    new_hdr = hdu_hdr.copy()
    # Offset
    new_hdr['CRVAL1'] = ra
    new_hdr['CRVAL2'] = dec
    new_hdr['CRPIX1'] = x
    new_hdr['CRPIX2'] = y
    return new_hdr

def offset_radec(hdu_hdr, ra_offset, dec_offset):
    """
    Impose offset on the header

    Args:
        hdu_hdr: Header
        ra_offset: float (deg)
        dec_offset:  float (deg)

    Returns:
        new_hdr : Header
    """
    new_hdr = hdu_hdr.copy()
    # Offset
    new_hdr['CRVAL1'] += ra_offset
    new_hdr['CRVAL2'] += dec_offset
    # Return
    return new_hdr

###Add the CD3_3 and CDELT3 keywords to a cube made by montage
def fix_kcwi_cube_montage(mosaicfil):
    hdu = fits.open(mosaicfil)
    flux = hdu['PRIMARY'].data
    hdu_hdr = hdu['PRIMARY'].header
    crval3 = hdu_hdr['CRVAL3']
    crpix3 = hdu_hdr['CRPIX3']
    cdelt3 = hdu_hdr['CDELT3']

    hdu_hdr['CDELT3'] = 1.0
    hdu_hdr['CD3_3'] = 1.0

    hdu_out = fits.PrimaryHDU(flux, header=hdu_hdr)
    hdu_out.writeto(mosaicfil, overwrite=True)


###Add the CD3_3 and CDELT3 keywords to a cube made by montage for higher resolution
def fix_kcwi_cube_montage_2(mosaicfil):
    hdu = fits.open(mosaicfil)
    flux = hdu['PRIMARY'].data
    hdu_hdr = hdu['PRIMARY'].header
    crval3 = hdu_hdr['CRVAL3']
    crpix3 = hdu_hdr['CRPIX3']
    cdelt3 = hdu_hdr['CDELT3']

    hdu_hdr['CDELT3'] = 0.5
    hdu_hdr['CD3_3'] = 0.5

    hdu_out = fits.PrimaryHDU(flux, header=hdu_hdr)
    hdu_out.writeto(mosaicfil, overwrite=True)


def airtovac(wave):
    """ Convert air-based wavelengths to vacuum

    Parameters:
    ----------
    wave: ndarray
      Wavelengths

    Returns:
    ----------
    wavelenght: ndarray
      Wavelength array corrected to vacuum wavelengths
    """
    # Assume AA
    wavelength = wave

    # Standard conversion format
    sigma_sq = (1.e4/wavelength)**2. #wavenumber squared
    factor = 1 + (5.792105e-2/(238.0185-sigma_sq)) + (1.67918e-3/(57.362-sigma_sq))
    factor = factor*(wavelength>=2000.) + 1.*(wavelength<2000.) #only modify above 2000A

    # Convert
    wavelength = wavelength*factor

    return wavelength



