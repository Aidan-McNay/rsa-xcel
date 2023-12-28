#=========================================================================
# MontModExp_test
#=========================================================================

import pytest

from random import randint, seed

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from rsa_xcel_mont.MontModExp import MontModExp

#-------------------------------------------------------------------------
# mod_exp
#-------------------------------------------------------------------------
# Python function for calculating modular exponentiation, to serve as an
# FL model

def mod_exp( base, exponent, modulus ):

    # Adapted from Schneier, Bruce (1996). Applied Cryptography: Protocols, Algorithms, and Source Code in C, Second Edition (2nd ed.)

    result = 1
    base = base % modulus

    while( exponent > 0 ):

        if( ( exponent % 2 ) == 1 ):
            result = ( result * base ) % modulus
        
        exponent = exponent >> 1
        base = ( base * base ) % modulus

    return result

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, modexp ):

    # Instantiate models

    s.src     = StreamSourceFL( mk_bits( 96 ) )
    s.sink    = StreamSinkFL( Bits32 )
    s.modexp  = modexp

    # Connect

    s.src.ostream    //= s.modexp.istream
    s.modexp.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.modexp.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

# Make input message, truncate ints to ensure they fit in 32 bits.

def mk_imsg( base, exponent, modulus ):
  return concat( Bits32( modulus, trunc_int=True ), Bits32( exponent, trunc_int=True ), Bits32( base, trunc_int=True ) )

# Make output message, truncate ints to ensure they fit in 32 bits.

def mk_omsg( a ):
  return Bits32( a, trunc_int=True )

#----------------------------------------------------------------------
# Test Cases 
#----------------------------------------------------------------------

simple_msgs = [
    mk_imsg(  9,  6, 11 ), mk_omsg(  9 ),
    mk_imsg( 13, 17, 21 ), mk_omsg( 13 ),
    mk_imsg(  3,  6, 15 ), mk_omsg(  9 ),
    mk_imsg(  5, 43, 39 ), mk_omsg(  8 ),
    mk_imsg( 17, 30, 41 ), mk_omsg(  9 ),
    mk_imsg( 37, 20, 43 ), mk_omsg( 36 ),
]

large_msgs = [
    mk_imsg( 0xa9e47e8b, 0x61e5784b, 0xcb35aebb ), mk_omsg( 0x314ef3a7 ),
    mk_imsg( 0x4b854680, 0x6300bd40, 0xa41abd2f ), mk_omsg( 0x2cce5ce2 ),
    mk_imsg( 0x0c9276d8, 0xe96e0299, 0x53e3327f ), mk_omsg( 0x190d01bd ),
    mk_imsg( 0x49251dbd, 0x6d8fbc06, 0x7a689f35 ), mk_omsg( 0x3520512a ),
    mk_imsg( 0x621b35b0, 0x7801b880, 0x9f293121 ), mk_omsg( 0x4d90e11f ),
    mk_imsg( 0x5508935e, 0x9cfad9bc, 0xe6eb1037 ), mk_omsg( 0xcb3dd4f9 ),
    mk_imsg( 0xabcdef00, 0xffffffff, 0xffffffff ), mk_omsg( 0xadf3e54b ),
]

# Random

# To ensure reproducible testing

seed(0xdeadbeef)

random_small_msgs = []
for i in range(10):
  b = randint(0,100)
  e = randint(0,100)
  n = randint(3,100)

  # Make sure n is odd and not 1, to satisfy prerequisite

  while( n % 2 == 0 ):
    n = randint(3,4294967295)
  
  random_small_msgs.extend( [ mk_imsg( b, e, n ), mk_omsg( mod_exp( b, e, n ) ) ] )

random_large_msgs = []
for i in range(10):
  b = randint(0,4294967295) # 4294967295 = 2^32 - 1 (the maximum 32-bit number)
  e = randint(0,4294967295)
  n = randint(3,4294967295)

  # Make sure n is odd and not 1, to satisfy prerequisite

  while( n % 2 == 0 ):
    n = randint(3,4294967295)
  
  random_large_msgs.extend( [ mk_imsg( b, e, n ), mk_omsg( mod_exp( b, e, n ) ) ] )


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

  th = TestHarness( MontModExp() )

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

  run_sim( th, cmdline_opts, duts=['modexp'] )

