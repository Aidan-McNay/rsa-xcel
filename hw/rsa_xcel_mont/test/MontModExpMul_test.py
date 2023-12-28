#=========================================================================
# ModExp_test
#=========================================================================

import pytest

from random import randint, seed

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from rsa_xcel_mont.MontModExpMul import MontModExpMul
from rsa_xcel_mont.test.MontMultiplier import MontMultiplier

#-------------------------------------------------------------------------
# mod_exp_mul
#-------------------------------------------------------------------------
# Python function for calculating the multiplication in Montgomery modular 
# exponentiation, to serve as an FL model
#
# Note: this is the same as our algorithm, but without the conversion

def mod_exp_mul( base, exponent, modulus, result_in ):

    # Adapted from Schneier, Bruce (1996). Applied Cryptography: Protocols, Algorithms, and Source Code in C, Second Edition (2nd ed.)
    # Using Montgomery multiplication

    result = result_in

    # Set up Montgomery multiplier

    MontMult = MontMultiplier( modulus, ( 1 << 32 ) )

    while( exponent > 0 ):

        if( ( exponent % 2 ) == 1 ):
            result = MontMult.multiply( result, base )
        
        exponent = exponent >> 1
        base = MontMult.multiply( base, base )
    
    return result

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, modexpmul ):

    # Instantiate models

    s.src        = StreamSourceFL( mk_bits( 128 ) )
    s.sink       = StreamSinkFL( Bits64 )
    s.modexpmul  = modexpmul

    # Connect

    s.src.ostream       //= s.modexpmul.istream
    s.modexpmul.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.modexpmul.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

# Make input message, truncate ints to ensure they fit in 32 bits.

def mk_imsg( base, exponent, modulus, result_in ):
  return concat( Bits32( result_in, trunc_int=True ), \
                 Bits32( modulus,   trunc_int=True ), \
                 Bits32( exponent,  trunc_int=True ), \
                 Bits32( base,      trunc_int=True ) )

# Make output message, truncate ints to ensure they fit in 32 bits.

def mk_omsg( result, n ):
  return concat( Bits32( n, trunc_int=True ), Bits32( result, trunc_int=True ) )

#----------------------------------------------------------------------
# Test Cases 
#----------------------------------------------------------------------

simple_msgs = [
    mk_imsg( 10,  6,  9, 33 ), mk_omsg(  6,  9 ),
    mk_imsg( 20, 17, 13,  3 ), mk_omsg( 11, 13 ),
    mk_imsg(  3,  6, 73, 50 ), mk_omsg( 12, 73 ),
    mk_imsg(  5, 43, 39, 42 ), mk_omsg( 33, 39 ),
    mk_imsg( 40, 30, 17, 26 ), mk_omsg( 13, 17 ),
    mk_imsg( 37, 20, 41,  6 ), mk_omsg(  6, 41 ),
]

large_msgs = [
    mk_imsg( 0xa9e47e8b, 0x61e5784b, 0x6b35aebb, 0x8950b4c8 ), mk_omsg( 0x32fe1c1c, 0x6b35aebb ),
    mk_imsg( 0x4b854680, 0x6300bd40, 0xa41abd2f, 0x014d5177 ), mk_omsg( 0x4bc5ad91, 0xa41abd2f ),
    mk_imsg( 0x0c9276d8, 0xe96e0299, 0x53e3327f, 0x02549dc8 ), mk_omsg( 0x2cf17f75, 0x53e3327f ),
    mk_imsg( 0x49251dbd, 0x6d8fbc06, 0x3a689f35, 0x0cd723ae ), mk_omsg( 0x2bb41dd4, 0x3a689f35 ),
    mk_imsg( 0x621b35b0, 0x7801b880, 0x9f293121, 0x3c16739f ), mk_omsg( 0x05d6ea75, 0x9f293121 ),
    mk_imsg( 0x5508935e, 0x9cfad9bc, 0xe6eb1037, 0x4681a664 ), mk_omsg( 0x268f8177, 0xe6eb1037 ),
    mk_imsg( 0xffffffff, 0xffffffff, 0xffffffff, 0x8a8c097d ), mk_omsg( 0xffffffff, 0xffffffff ),
]

# Random

# To ensure reproducible testing

seed(0xdeadbeef)

random_small_msgs = []
for i in range(10):
  b = randint(0,100)
  e = randint(0,100)
  n = randint(3,100)
  r = 1

  # Make sure n is odd and not 1, to satisfy prerequisite

  while( n % 2 == 0 ):
    n = randint(3,4294967295)

  # Convert in

  multiplier = MontMultiplier( n, 2 ** 32 )
  b = multiplier.convert_in( b )
  r = multiplier.convert_in( r )
  
  random_small_msgs.extend( [ mk_imsg( b, e, n, r ), mk_omsg( mod_exp_mul( b, e, n, r ), n ) ] )

random_large_msgs = []
for i in range(10):
  b = randint(0,4294967295) # 4294967295 = 2^32 - 1 (the maximum 32-bit number)
  e = randint(0,4294967295)
  n = randint(3,4294967295)
  r = 1

  # Make sure n is odd and not 1, to satisfy prerequisite

  while( n % 2 == 0 ):
    n = randint(3,4294967295)

  # Convert in

  multiplier = MontMultiplier( n, 2 ** 32 )
  b = multiplier.convert_in( b )
  r = multiplier.convert_in( r )
  
  random_large_msgs.extend( [ mk_imsg( b, e, n, r ), mk_omsg( mod_exp_mul( b, e, n, r ), n ) ] )


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

  th = TestHarness( MontModExpMul() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )
  
  # Increase maximum cycles for testing

  cmdline_opts["max_cycles"] = 100000

  run_sim( th, cmdline_opts, duts=['modexpmul'] )

