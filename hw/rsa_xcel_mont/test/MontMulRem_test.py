#=========================================================================
# MontMulRem_test
#=========================================================================

import pytest

from random import randint, seed

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from rsa_xcel_mont.MontMulRem import MontMulRem
from rsa_xcel_mont.test.MontMultiplier import MontMultiplier

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, mulrem ):

    # Instantiate models

    s.src     = StreamSourceFL( mk_bits( 96 ) )
    s.sink    = StreamSinkFL( Bits32 )
    s.mulrem  = mulrem

    # Connect

    s.src.ostream    //= s.mulrem.istream
    s.mulrem.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.mulrem.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

# Make input message, truncate ints to ensure they fit in 32 bits.

def mk_imsg( opa, opb, modulus ):
  return concat( Bits32( modulus, trunc_int=True ), Bits32( opa, trunc_int=True ), Bits32( opb, trunc_int=True ) )

# Make output message, truncate ints to ensure they fit in 32 bits.

def mk_omsg( a ):
  return Bits32( a, trunc_int=True )

#----------------------------------------------------------------------
# Test Cases 
#----------------------------------------------------------------------

simple_msgs = [
    mk_imsg(  7,  6,  9 ), mk_omsg(  6 ),
    mk_imsg( 11, 10, 13 ), mk_omsg(  5 ),
    mk_imsg(  6, 54, 73 ), mk_omsg(  1 ),
    mk_imsg(  2, 25, 39 ), mk_omsg( 20 ),
    mk_imsg(  6, 13, 17 ), mk_omsg( 10 ),
    mk_imsg( 18, 33, 41 ), mk_omsg( 36 ),
]

large_msgs = [
    mk_imsg( 0xa9e47e8b, 0x61e5784b, 0x6b35aebb ), mk_omsg( 0x47800bd2 ),
    mk_imsg( 0x4b854680, 0x6300bd40, 0xa41abd2f ), mk_omsg( 0x2bccc756 ),
    mk_imsg( 0x0c9276d8, 0xe96e0299, 0x53e3327f ), mk_omsg( 0x3443aab8 ),
    mk_imsg( 0x49251dbd, 0x6d8fbc06, 0x3a689f35 ), mk_omsg( 0x24be0ebc ),
    mk_imsg( 0x621b35b0, 0x7801b880, 0x9f293121 ), mk_omsg( 0x3fde51db ),
    mk_imsg( 0x5508935e, 0x9cfad9bc, 0xe6eb1037 ), mk_omsg( 0xc88dd246 ),
    mk_imsg( 0xffffffff, 0xffffffff, 0xffffffff ), mk_omsg( 0xffffffff ),
]

# Random

# To ensure reproducible testing

seed(0xdeadbeef)

random_small_msgs = []
for i in range(50):
  a = randint(0,100)
  b = randint(0,100)
  c = randint(3,100)

  # Make sure c is odd and not 1, to satisfy prerequisite

  while( c % 2 == 0 ):
    c = randint(3,100)

  # Calculate correct result

  multiplier = MontMultiplier( c, 2 ** 32 )
  a = multiplier.convert_in( a )
  b = multiplier.convert_in( b )

  result = multiplier.multiply( a, b )
  
  random_small_msgs.extend( [ mk_imsg( a, b, c ), mk_omsg( result ) ] )

random_large_msgs = []
for i in range(50):
  a = randint(0,4294967295) # 4294967295 = 2^32 - 1 (the maximum 32-bit number)
  b = randint(0,4294967295)
  c = randint(3,4294967295)

  # Make sure c is odd and not 1, to satisfy prerequisite

  while( c % 2 == 0 ):
    c = randint(3,4294967295)

  # Calculate correct result

  multiplier = MontMultiplier( c, 2 ** 32 )
  a = multiplier.convert_in( a )
  b = multiplier.convert_in( b )

  result = multiplier.multiply( a, b )
  
  random_large_msgs.extend( [ mk_imsg( a, b, c ), mk_omsg( result ) ] )


#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                                         "msgs       src_delay     sink_delay"),
  [          "simple_msgs",             simple_msgs,              0,             0 ],
  [          "simple_msgs",             simple_msgs,             40,             0 ],
  [          "simple_msgs",             simple_msgs,              0,            40 ],
  [          "simple_msgs",             simple_msgs,             40,            40 ],
  [          "simple_msgs",             simple_msgs,             60,            40 ],
  [          "simple_msgs",             simple_msgs,             40,            60 ],

  [           "large_msgs",              large_msgs,              0,             0 ],
  [           "large_msgs",              large_msgs,             40,             0 ],
  [           "large_msgs",              large_msgs,              0,            40 ],
  [           "large_msgs",              large_msgs,             40,            40 ],
  [           "large_msgs",              large_msgs,             60,            40 ],
  [           "large_msgs",              large_msgs,             40,            60 ],
  
  [         "random_small",       random_small_msgs,              0,             0 ],
  [         "random_small",       random_small_msgs,             40,             0 ],
  [         "random_small",       random_small_msgs,              0,            40 ],
  [         "random_small",       random_small_msgs,             40,            40 ],
  [         "random_small",       random_small_msgs,             60,            40 ],
  [         "random_small",       random_small_msgs,             40,            60 ],

  [         "random_large",       random_large_msgs,              0,             0 ],
  [         "random_large",       random_large_msgs,             40,             0 ],
  [         "random_large",       random_large_msgs,              0,            40 ],
  [         "random_large",       random_large_msgs,             40,            40 ],
  [         "random_large",       random_large_msgs,             60,            40 ],
  [         "random_large",       random_large_msgs,             40,            60 ],

])


#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, cmdline_opts ):

  th = TestHarness( MontMulRem() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  run_sim( th, cmdline_opts, duts=['mulrem'] )

