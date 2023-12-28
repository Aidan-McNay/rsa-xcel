#=========================================================================
# RSAMontXcel_test
#=========================================================================

import pytest

from rsa_xcel_naive.test.RSAXcelFL_test import test_case_table, run_test
from rsa_xcel_mont.RSAMontXcel import RSAMontXcel

@pytest.mark.parametrize( **test_case_table )
def test( cmdline_opts, test_params ):
  run_test( RSAMontXcel(), cmdline_opts, test_params )

