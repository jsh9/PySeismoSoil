# Author: Jian Shi

import unittest
import numpy as np

import PySeismoSoil.helper_hh_model as hh

class Test_Helper_HH_Model(unittest.TestCase):
    '''
    Unit tests for helper functions in helper_hh_model.py
    '''

    def __init__(self, methodName='runTest'):
        self.strain = np.logspace(-2, 1, num=12)
        self.atol = 1e-4
        self.param = {'gamma_t': 0.1, 'a': 0.2, 'gamma_ref': 0.3, 'beta': 0.4,
                      's': 0.5, 'Gmax': 0.6, 'mu': 0.7, 'Tmax': 0.8, 'd': 0.9}
        self.array = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]) / 10.0
        super(Test_Helper_HH_Model, self).__init__(methodName=methodName)

    def test_tau_MKZ(self):
        T = hh.tau_MKZ(self.strain, gamma_ref=1, beta=2, s=3, Gmax=4)
        # note: benchmark results come from comparable functions in MATLAB
        self.assertTrue(np.allclose(T, [0.0400, 0.0750, 0.1404, 0.2630, 0.4913,
                                        0.9018, 1.4898, 1.5694, 0.7578, 0.2413,
                                        0.0700, 0.0200], atol=self.atol))

    def test_tau_FKZ(self):
        T = hh.tau_FKZ(self.strain, Gmax=4, mu=3, d=2, Tmax=1)
        self.assertTrue(np.allclose(T, [0.0012, 0.0042, 0.0146, 0.0494, 0.1543,
                                        0.3904, 0.6922, 0.8876, 0.9652, 0.9898,
                                        0.9971, 0.9992], atol=self.atol))

    def test_transition_function(self):
        w = hh.transition_function(self.strain, a=3, gamma_t=0.05)
        self.assertTrue(np.allclose(w, [1.0000, 1.0000, 1.0000, 0.9997, 0.9980,
                                        0.9872, 0.9216, 0.6411, 0.2136, 0.0396,
                                        0.0062, 0.0010], atol=self.atol))

    def test_tau_HH(self):
        T = hh.tau_HH(self.strain, gamma_t=1, a=2, gamma_ref=3, beta=4, s=5,
                      Gmax=6, mu=7, Tmax=8, d=9)
        self.assertTrue(np.allclose(T, [0.0600, 0.1124, 0.2107, 0.3948, 0.7397,
                                        1.3861, 2.5966, 4.8387, 8.0452, 4.1873,
                                        0.4678, 0.1269], atol=self.atol))

    def test_calc_damping_from_param(self):
        xi = hh.calc_damping_from_param(self.param, self.strain)
        self.assertTrue(np.allclose(xi, [0.0000, 0.0085, 0.0139, 0.0192, 0.0256,
                                         0.0334, 0.0430, 0.0544, 0.0675, 0.0820,
                                         0.0973, 0.1128], atol=self.atol))

    def test_serialize_params_to_array(self):
        array = hh.serialize_params_to_array(self.param)
        self.assertTrue(np.allclose(array, self.array))

    def test_deserialize_array_to_params(self):
        param = hh.deserialize_array_to_params(self.array)
        self.assertEqual(param, self.param)

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(Test_Helper_HH_Model)
    unittest.TextTestRunner(verbosity=2).run(SUITE)