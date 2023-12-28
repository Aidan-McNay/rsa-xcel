#=========================================================================
# SortXcelFL_test
#=========================================================================

import pytest
import random
import struct

random.seed(0xdeadbeef)

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream     import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.xcel       import XcelMsgType, mk_xcel_msg

from rsa.core import encrypt_int
from rsa      import newkeys

from random import randint, seed
seed( 0xdeadbeef )

from rsa_xcel_naive.RSAXcelFL import RSAXcelFL

XcelReqMsg, XcelRespMsg = mk_xcel_msg( 5, 32 )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, xcel ):

    s.src  = StreamSourceFL( XcelReqMsg )
    s.sink = StreamSinkFL( XcelRespMsg )
    s.xcel = xcel

    s.src.ostream  //= s.xcel.xcel.reqstream
    s.sink.istream //= s.xcel.xcel.respstream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.xcel.line_trace() + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# make messages
#-------------------------------------------------------------------------

def xreq( type_, raddr, data ):
  if type_ == 'rd':
    return XcelReqMsg( XcelMsgType.READ, raddr, data )
  else:
    return XcelReqMsg( XcelMsgType.WRITE, raddr, data )

def xresp( type_, data ):
  if type_ == 'rd':
    return XcelRespMsg( XcelMsgType.READ, data )
  else:
    return XcelRespMsg( XcelMsgType.WRITE, data )

#-------------------------------------------------------------------------
# Xcel Protocol
#-------------------------------------------------------------------------
# These are the source sink messages we need to configure the accelerator
# and wait for it to finish. We use the same messages in all of our
# tests. The difference between the tests is the data to be sorted in the
# test memory.

def gen_xcel_protocol_msgs( base, exp, mod ):
  return [
    xreq( 'wr', 1, base      ), xresp( 'wr',                             0 ),
    xreq( 'wr', 2, exp       ), xresp( 'wr',                             0 ),
    xreq( 'wr', 3, mod       ), xresp( 'wr',                             0 ),
    xreq( 'wr', 0, 0         ), xresp( 'wr',                             0 ),
    xreq( 'rd', 0, 0         ), xresp( 'rd', encrypt_int( base, exp, mod ) ),
  ]

#-------------------------------------------------------------------------
# Test Cases
#-------------------------------------------------------------------------

small_data  = []
small_data += gen_xcel_protocol_msgs( 23, 65537, 2671158053 )
small_data += gen_xcel_protocol_msgs( 41, 65537, 2763811321 )
small_data += gen_xcel_protocol_msgs( 28, 65537, 2380901689 )
small_data += gen_xcel_protocol_msgs( 29, 65537, 3074026273 )
small_data += gen_xcel_protocol_msgs( 34, 65537, 2540810791 )
small_data += gen_xcel_protocol_msgs( 18, 65537, 2639392183 )

large_data  = []
large_data += gen_xcel_protocol_msgs( 0x19160f90, 65537, 2671158053 )
large_data += gen_xcel_protocol_msgs( 0x30a5fce0, 65537, 2763811321 )
large_data += gen_xcel_protocol_msgs( 0x6fab4778, 65537, 2380901689 )
large_data += gen_xcel_protocol_msgs( 0x2c0f5fa7, 65537, 3074026273 )
large_data += gen_xcel_protocol_msgs( 0x33128e5f, 65537, 2540810791 )
large_data += gen_xcel_protocol_msgs( 0x017b30d3, 65537, 2639392183 )

random_data = []
for i in range( 10 ):
  keys = newkeys( 32 )
  pub_key = keys[0]

  n = pub_key.n
  e = pub_key.e
  message = randint( 0, n - 1 )
  random_data += gen_xcel_protocol_msgs( message, e, n )

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
                         #                delays   test mem
                         #                -------- ---------
  (                      "data            src sink stall lat"),
  [ "small_data",         small_data,     0,  0,   0,    0   ],
  [ "large_data",         large_data,     0,  0,   0,    0   ],
  [ "random_data",        random_data,    0,  0,   0,    0   ],
  [ "random_data_3x14x0", random_data,    3, 14,   0,    0   ],
  [ "random_data_5x7x0",  random_data,    5,  7,   0,    0   ],
  [ "random_data_0x0x4",  random_data,    0,  0,   0.5,  4   ],
  [ "random_data_3x14x4", random_data,    3,  14,  0.5,  4   ],
  [ "random_data_5x7x4",  random_data,    5,  7,   0.5,  4   ],
])

#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------

def run_test( xcel, cmdline_opts, test_params ):

  data = test_params.data

  # Protocol messages

  xreqs  = data[::2]
  xresps = data[1::2]

  # Create test harness with protocol messagse

  th = TestHarness( xcel )

  th.set_param( "top.src.construct", msgs=xreqs,
    initial_delay=test_params.src+3, interval_delay=test_params.src )

  th.set_param( "top.sink.construct", msgs=xresps,
    initial_delay=test_params.sink+3, interval_delay=test_params.sink )

  th.elaborate()

  # Enlarge max_cycles

  if cmdline_opts['max_cycles'] is None:
    cmdline_opts['max_cycles'] = 100000

  # Run the test

  run_sim( th, cmdline_opts, duts=['xcel'] )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( cmdline_opts, test_params ):
  run_test( RSAXcelFL(), cmdline_opts, test_params )

