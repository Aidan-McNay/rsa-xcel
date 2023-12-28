#=========================================================================
# MontMulRem_test
#=========================================================================

import pytest

from random import randint, seed

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from rsa_xcel_mont.MontConvertOut import MontConvertOut
from rsa_xcel_mont.test.MontMultiplier import MontMultiplier

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, converter ):

    # Instantiate models

    s.src        = StreamSourceFL( Bits64 )
    s.sink       = StreamSinkFL( Bits32 )
    s.converter  = converter

    # Connect

    s.src.ostream       //= s.converter.istream
    s.converter.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.converter.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

# Make input message, truncate ints to ensure they fit in 32 bits.

def mk_imsg( result, n ):
  return concat( Bits32( n, trunc_int=True ), Bits32( result, trunc_int=True ) )

# Make output message, truncate ints to ensure they fit in 32 bits.

def mk_omsg( a ):
  return Bits32( a, trunc_int=True )

#----------------------------------------------------------------------
# Test Cases 
#----------------------------------------------------------------------

simple_msgs = [
    mk_imsg(  6,  9 ), mk_omsg(  6 ),
    mk_imsg( 10, 13 ), mk_omsg(  4 ),
    mk_imsg( 54, 73 ), mk_omsg( 61 ),
    mk_imsg( 25, 39 ), mk_omsg( 10 ),
    mk_imsg( 13, 17 ), mk_omsg( 13 ),
    mk_imsg( 33, 41 ), mk_omsg(  2 ),
]

large_msgs = [
    mk_imsg( 0x61e5784b, 0x6b35aebb ), mk_omsg( 0x3314af4f ),
    mk_imsg( 0x6300bd40, 0xa41abd2f ), mk_omsg( 0x6ccb6cc2 ),
    mk_imsg( 0xe96e0299, 0x53e3327f ), mk_omsg( 0x370560e7 ),
    mk_imsg( 0x6d8fbc06, 0x3a689f35 ), mk_omsg( 0x10179877 ),
    mk_imsg( 0x7801b880, 0x9f293121 ), mk_omsg( 0x09cd2c3d ),
    mk_imsg( 0x9cfad9bc, 0xe6eb1037 ), mk_omsg( 0xaf1f83f1 ),
    mk_imsg( 0xffffffff, 0xffffffff ), mk_omsg( 0xffffffff ),
]

# Random

# To ensure reproducible testing

seed(0xdeadbeef)

random_small_msgs = []
for i in range(50):
  r = randint(0,100)
  n = randint(3,100)

  # Make sure n is odd and not 1, to satisfy prerequisite

  while( n % 2 == 0 ):
    n = randint(3,100)

  # Calculate correct result

  multiplier = MontMultiplier( n, 2 ** 32 )
  r_conv = multiplier.convert_out( r )
  
  random_small_msgs.extend( [ mk_imsg( r, n ), mk_omsg( r_conv ) ] )

random_large_msgs = []
for i in range(50):
  r = randint(0,4294967295) # 4294967295 = 2^32 - 1 (the maximum 32-bit number)
  n = randint(3,4294967295)

  # Make sure n is odd and not 1, to satisfy prerequisite

  while( n % 2 == 0 ):
    n = randint(3,4294967295)

  # Calculate correct result

  multiplier = MontMultiplier( n, 2 ** 32 )
  r_conv = multiplier.convert_out( r )
  
  random_large_msgs.extend( [ mk_imsg( r, n ), mk_omsg( r_conv ) ] )


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

  th = TestHarness( MontConvertOut() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  run_sim( th, cmdline_opts, duts=['converter'] )

