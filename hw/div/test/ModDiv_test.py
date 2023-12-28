#=========================================================================
# ModDiv_test
#=========================================================================

import pytest

from random import randint, seed

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from div.ModDiv import ModDiv

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, div ):

    # Instantiate models

    s.src  = StreamSourceFL( mk_bits( 65 ) )
    s.sink = StreamSinkFL( Bits32 )
    s.div  = div

    # Connect

    s.src.ostream //= s.div.istream
    s.div.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.div.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

# Make input message, truncate ints to ensure they fit in 32 bits.

def mk_imsg( a, b, output_type ):

  sel_val = 0
  if( output_type == "rem" ):
    sel_val = 1

  return concat( Bits1( sel_val ), Bits32( a, trunc_int=True ), Bits32( b, trunc_int=True ) )

# Make output message, truncate ints to ensure they fit in 32 bits.

def mk_omsg( a ):
  return Bits32( a, trunc_int=True )

#----------------------------------------------------------------------
# Test Cases 
#----------------------------------------------------------------------

simple_div_msgs = [
    mk_imsg(   6,   3, "div" ), mk_omsg( 2 ),
    mk_imsg(  13,   4, "div" ), mk_omsg( 3 ),
    mk_imsg(  69,  14, "div" ), mk_omsg( 4 ),
    mk_imsg(   0,   5, "div" ), mk_omsg( 0 ),
    mk_imsg(  15,  21, "div" ), mk_omsg( 0 ),
    mk_imsg( 693, 107, "div" ), mk_omsg( 6 ),
]

simple_rem_msgs = [
    mk_imsg(   6,   3, "rem" ), mk_omsg(  0 ),
    mk_imsg(  13,   4, "rem" ), mk_omsg(  1 ),
    mk_imsg(  69,  14, "rem" ), mk_omsg( 13 ),
    mk_imsg(   0,   5, "rem" ), mk_omsg(  0 ),
    mk_imsg(  15,  21, "rem" ), mk_omsg( 15 ),
    mk_imsg( 693, 107, "rem" ), mk_omsg( 51 ),
]

large_div_msgs = [
    mk_imsg( 0xeab9518d, 0x0ca6f9bc, "div" ), mk_omsg( 18 ),
    mk_imsg( 0xa8d0998d, 0x032a2cf2, "div" ), mk_omsg( 53 ),
    mk_imsg( 0x50d235fa, 0x03ab726e, "div" ), mk_omsg( 22 ),
    mk_imsg( 0xedf34992, 0x0d5eb27c, "div" ), mk_omsg( 17 ),
    mk_imsg( 0x25a1f969, 0x0e79257d, "div" ), mk_omsg(  2 ),
    mk_imsg( 0x9aa29494, 0x04eb6d56, "div" ), mk_omsg( 31 ),
]

large_rem_msgs = [
    mk_imsg( 0x87ccfa10, 0x0af3e000, "rem" ), mk_omsg( 0x045e7a10 ),
    mk_imsg( 0xb7b18e5c, 0x035c97fc, "rem" ), mk_omsg( 0x02297f34 ),
    mk_imsg( 0x8e430c5c, 0x0a7a97c1, "rem" ), mk_omsg( 0x0609578f ),
    mk_imsg( 0xd8d24908, 0x01cab04e, "rem" ), mk_omsg( 0x0004f42a ),
    mk_imsg( 0xe750f871, 0x0cab301b, "rem" ), mk_omsg( 0x0347968b ),
    mk_imsg( 0x46e49037, 0x04eb8add, "rem" ), mk_omsg( 0x0202f821 ),
]

interleaved_msgs = [
    mk_imsg( 0x61def4fc, 0x065c95bb, "div" ), mk_omsg(         15 ),
    mk_imsg( 0x80dad9cb, 0x072d787b, "rem" ), mk_omsg( 0x06d5d9a0 ),
    mk_imsg( 0x7ea90e06, 0x0da04278, "div" ), mk_omsg(          9 ),
    mk_imsg( 0x4ff0e47f, 0x0fc9bd6f, "rem" ), mk_omsg( 0x01003154 ),
    mk_imsg( 0x25d47aad, 0x0e2eba43, "div" ), mk_omsg(          2 ),
    mk_imsg( 0x2ef961cd, 0x08b6ff26, "rem" ), mk_omsg( 0x0366660f ),
    mk_imsg( 0xcf24356e, 0x0a6d6e6b, "div" ), mk_omsg(         19 ),
    mk_imsg( 0xe5f17976, 0x09e7a04a, "rem" ), mk_omsg( 0x022212d0 ),
]

# Random

# To ensure reproducible testing

seed(0xdeadbeef)

random_small_msgs = []
for i in range(50):
  a = randint(0,100)
  b = randint(0,100)
  msg_sel = randint( 0, 1 )
  if( msg_sel == 0 ):
    random_small_msgs.extend( [ mk_imsg( a, b, "div" ), mk_omsg( a // b ) ] )
  else:
    random_small_msgs.extend( [ mk_imsg( a, b, "rem" ), mk_omsg( a % b ) ] )

random_large_msgs = []
for i in range(50):
  a = randint(0,4294967295) # 4294967295 = 2^32 - 1 (the maximum 32-bit number)
  b = randint(0,4294967295)
  msg_sel = randint( 0, 1 )
  if( msg_sel == 0 ):
    random_large_msgs.extend( [ mk_imsg( a, b, "div" ), mk_omsg( a // b ) ] )
  else:
    random_large_msgs.extend( [ mk_imsg( a, b, "rem" ), mk_omsg( a % b ) ] )


#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                                         "msgs       src_delay     sink_delay"),
  [           "simple_div",         simple_div_msgs,              0,             0 ],
  [           "simple_div",         simple_div_msgs,             40,             0 ],
  [           "simple_div",         simple_div_msgs,              0,            40 ],
  [           "simple_div",         simple_div_msgs,             40,            40 ],
  [           "simple_div",         simple_div_msgs,             60,            40 ],
  [           "simple_div",         simple_div_msgs,             40,            60 ],

  [           "simple_rem",         simple_rem_msgs,              0,             0 ],
  [           "simple_rem",         simple_rem_msgs,             40,             0 ],
  [           "simple_rem",         simple_rem_msgs,              0,            40 ],
  [           "simple_rem",         simple_rem_msgs,             40,            40 ],
  [           "simple_rem",         simple_rem_msgs,             60,            40 ],
  [           "simple_rem",         simple_rem_msgs,             40,            60 ],

  [            "large_div",          large_div_msgs,              0,             0 ],
  [            "large_div",          large_div_msgs,             40,             0 ],
  [            "large_div",          large_div_msgs,              0,            40 ],
  [            "large_div",          large_div_msgs,             40,            40 ],
  [            "large_div",          large_div_msgs,             60,            40 ],
  [            "large_div",          large_div_msgs,             40,            60 ],

  [            "large_rem",          large_rem_msgs,              0,             0 ],
  [            "large_rem",          large_rem_msgs,             40,             0 ],
  [            "large_rem",          large_rem_msgs,              0,            40 ],
  [            "large_rem",          large_rem_msgs,             40,            40 ],
  [            "large_rem",          large_rem_msgs,             60,            40 ],
  [            "large_rem",          large_rem_msgs,             40,            60 ],

  [          "interleaved",        interleaved_msgs,              0,             0 ],
  [          "interleaved",        interleaved_msgs,             40,             0 ],
  [          "interleaved",        interleaved_msgs,              0,            40 ],
  [          "interleaved",        interleaved_msgs,             40,            40 ],
  [          "interleaved",        interleaved_msgs,             60,            40 ],
  [          "interleaved",        interleaved_msgs,             40,            60 ],

  
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

  th = TestHarness( ModDiv() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  run_sim( th, cmdline_opts, duts=['div'] )

