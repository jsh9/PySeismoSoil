# Author: Jian Shi

import numpy as np

from . import helper_site_response as sr

from .class_ground_motion import Ground_Motion
from .class_site_factors import Site_Factors

class Site_Effect_Adjustment():
    '''
    Adjusts rock-outcrop ground motions by applying site effect adjustment
    using the SAG19 site factors.

    Parameters
    ----------
    input_motion : class_ground_motion.Ground_Motion
        Input ground motion
    Vs30_in_meter_per_sec : float
        Vs30 values in SI unit
    z1_in_m : float
        z1 (basin depth) in meters. If None, it will be estimated from Vs30
        using the following correlation: z1 = 140.511 * exp(-0.00303 * Vs30),
        where the units of z1 and Vs30 are both SI units. This formula is
        obtained from the dataset used in Shi & Asimaki (2018).

    Attributes
    ----------
    input_motion : class_ground_motion.Ground_Motion
        Input ground motion
    Vs30 : float
        Vs30 of the site. (Unit: m/s)
    z1 : float
        z1 (basin depth) of the site. (Unit: m/s)
    PGA_in_g : float
        Peak ground acceleration of the input motion. (Unit: g)
    '''
    def __init__(self, input_motion, Vs30_in_meter_per_sec, z1_in_m=None,
                 ampl_method='nl_hh', lenient=False):

        if not isinstance(input_motion, Ground_Motion):
            raise TypeError('`input_motion` must be of class `Ground_Motion`.')
        if not isinstance(Vs30_in_meter_per_sec, (int, float, np.number)):
            raise TypeError('`Vs30_in_meter_per_sec` must be int, float, or '
                            'numpy.number.')
        if not isinstance(z1_in_m, (int, float, np.number, type(None))):
            raise TypeError('`z1_in_m` must be int, float, numpy.number, or '
                            'None.')
        if ampl_method not in {'nl_hh', 'eq_hh'}:
            raise ValueError("Currently, only 'nl_hh' and 'eq_hh' are valid.")

        if z1_in_m is None:
            z1_in_m = 140.511 * np.exp(-0.00303 * Vs30_in_meter_per_sec)
        PGA_in_g = input_motion.pga_in_g

        self.input_motion = input_motion
        self.Vs30 = Vs30_in_meter_per_sec
        self.z1 = z1_in_m
        self.PGA_in_g = PGA_in_g
        self._lenient = lenient
        self._ampl_method = ampl_method

    def run(self, show_fig=False, return_fig_obj=False, **kwargs_to_plot):
        '''
        Run the site effect adjustment by querying the SAG19 site factors.
        '''
        sf = Site_Factors(self.Vs30, self.z1, self.PGA_in_g,
                          lenient=self._lenient)
        af = sf.get_amplification(method=self._ampl_method, Fourier=True)
        phf = sf.get_phase_shift(method='eq_hh')  # only `eq_hh` is valid

        if not np.allclose(af.freq, phf.freq):
            print('Warning: the frequency arrays of the amplification factor '
                  'and the phase factor are not identical---something may '
                  'be wrong in class_site_factors.py.')
        if af.iscomplex:
            print('Warning: the amplification factor is complex, rather than '
                  'real---something may be wrong in class_site_factors.py')
        if phf.iscomplex:
            print('Warning: the phase factor is complex, rather than '
                  'real---something may be wrong in class_site_factors.py')

        freq = af.freq
        amp_tf = af.spectrum
        phase_tf = phf.spectrum

        accel_in = self.input_motion.accel  # acceleration in m/s/s
        result = sr.amplify_motion(accel_in, (freq, (amp_tf, phase_tf)),
                                   show_fig=show_fig, return_fig_obj=show_fig,
                                   extrap_tf=True, **kwargs_to_plot)
        if show_fig:
            accel_out, fig, ax = result
            ax[0].set_ylabel('Accel. [m/s/s]')
            ax[0].set_title('$V_{S30}$=%.1fm/s, $z_1$=%.1fm, '
                            '$\mathrm{PGA}_{\mathrm{input}}$=%.3g$g$' % \
                            (self.Vs30, self.z1, self.PGA_in_g))
        else:
            accel_out = result

        output_motion = Ground_Motion(accel_out, unit='m')
        if return_fig_obj:
            if not show_fig:
                fig, ax = None, None
            return output_motion, fig, ax
        else:
            return output_motion