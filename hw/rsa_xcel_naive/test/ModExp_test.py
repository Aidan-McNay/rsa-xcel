#=========================================================================
# ModExp_test
#=========================================================================

import pytest

from random import randint, seed

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL

from rsa_xcel_naive.ModExp import ModExp

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
    mk_imsg( 10,  6,  9 ), mk_omsg(  1 ),
    mk_imsg( 20, 17, 13 ), mk_omsg( 11 ),
    mk_imsg(  3,  6,  1 ), mk_omsg(  0 ),
    mk_imsg(  5, 43, 38 ), mk_omsg( 35 ),
    mk_imsg( 40, 30, 17 ), mk_omsg(  9 ),
    mk_imsg( 37, 20, 42 ), mk_omsg( 25 ),
]

large_msgs = [
    mk_imsg( 0xa9e47e8b, 0x61e5784b, 0x6b35aeba ), mk_omsg( 0x0c29469b ),
    mk_imsg( 0x4b854680, 0x6300bd40, 0xa41abd2e ), mk_omsg( 0x8fa77752 ),
    mk_imsg( 0x0c9276d8, 0xe96e0299, 0x53e3327e ), mk_omsg( 0x25d443da ),
    mk_imsg( 0x49251dbd, 0x6d8fbc06, 0x3a689f35 ), mk_omsg( 0x1487a318 ),
    mk_imsg( 0x621b35b0, 0x7801b880, 0x9f293121 ), mk_omsg( 0x4d90e11f ),
    mk_imsg( 0x5508935e, 0x9cfad9bc, 0xe6eb1036 ), mk_omsg( 0x8b0458d2 ),
    mk_imsg( 0xffffffff, 0xffffffff, 0xffffffff ), mk_omsg( 0x00000000 ),
]

# Random

# To ensure reproducible testing

seed(0xdeadbeef)

random_small_msgs = []
for i in range(10):
  b = randint(0,100)
  e = randint(0,100)
  n = randint(1,100)
  
  random_small_msgs.extend( [ mk_imsg( b, e, n ), mk_omsg( mod_exp( b, e, n ) ) ] )

random_large_msgs = []
for i in range(10):
  b = randint(0,4294967295) # 4294967295 = 2^32 - 1 (the maximum 32-bit number)
  e = randint(0,4294967295)
  n = randint(1,4294967295)
  
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

  th = TestHarness( ModExp() )

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

