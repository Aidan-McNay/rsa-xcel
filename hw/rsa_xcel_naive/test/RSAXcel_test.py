#=========================================================================
# RSAXcel_test
#=========================================================================

import pytest

from rsa_xcel_naive.test.RSAXcelFL_test import test_case_table, run_test
from rsa_xcel_naive.RSAXcel import RSAXcel

@pytest.mark.parametrize( **test_case_table )
def test( cmdline_opts, test_params ):
  run_test( RSAXcel(), cmdline_opts, test_params )

