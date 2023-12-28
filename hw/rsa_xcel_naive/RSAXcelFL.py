#=========================================================================
# RSA Xcel Unit FL Model
#=========================================================================
# RSA modular exponentiation accelerator
#
# Accelerator register interface:
#
#  xr0 : go/done
#  xr1 : base
#  xr2 : exponent
#  xr3 : modulus
#
# Accelerator protocol involves the following steps:
#  1. Write the base via xr1
#  2. Write the exponent via xr2
#  3. Write the modulus via xr3
#  4. Tell accelerator to go by writing xr0
#  5. Wait for accelerator to finish by reading xr0, result will be the
#     result of modular exponentiation
#

from pymtl3 import *
from pymtl3.stdlib.xcel.ifcs import XcelResponderIfc
from pymtl3.stdlib.xcel      import XcelMsgType, mk_xcel_msg
from pymtl3.stdlib.stream    import OStreamBlockingAdapterFL
from pymtl3.stdlib.stream    import IStreamBlockingAdapterFL

from rsa.core import encrypt_int

class RSAXcelFL( Component ):

  def construct( s ):

    XcelReqMsg, XcelRespMsg = mk_xcel_msg( 5, 32 )

    # Interface

    s.xcel = XcelResponderIfc( XcelReqMsg, XcelRespMsg )

    # Proc <-> Xcel Adapters

    s.xcelreq_q  = IStreamBlockingAdapterFL( XcelReqMsg  )
    s.xcelresp_q = OStreamBlockingAdapterFL( XcelRespMsg )

    connect( s.xcelreq_q.istream,  s.xcel.reqstream  )
    connect( s.xcelresp_q.ostream, s.xcel.respstream )

    # Storage

    s.base  = 0
    s.exp   = 0
    s.mod   = 0

    @update_once
    def up_sort_xcel():

      # We loop handling accelerator requests. We are only expecting
      # writes to xr0-2, so any other requests are an error. We exit the
      # loop when we see the write to xr0.

      go = False
      while not go:

        xcelreq_msg = s.xcelreq_q.deq()

        if xcelreq_msg.type_ == XcelMsgType.WRITE:
          assert xcelreq_msg.addr in [0,1,2,3], \
            "Only reg writes to 0,1,2,3 allowed during setup!"

          # Use xcel register address to configure accelerator

          if   xcelreq_msg.addr == 0: go = True
          elif xcelreq_msg.addr == 1: s.base  = xcelreq_msg.data
          elif xcelreq_msg.addr == 2: s.exp   = xcelreq_msg.data
          elif xcelreq_msg.addr == 3: s.mod   = xcelreq_msg.data

          # Send xcel response message

          s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.WRITE, 0 ) )

      # Compute result

      result = encrypt_int( int( s.base ), int( s.exp ), int( s.mod ) )

      # Now wait for read of xr0

      xcelreq_msg = s.xcelreq_q.deq()

      # Only expecting read from xr0, so any other request is an xcel
      # protocol error.

      assert xcelreq_msg.type_ == XcelMsgType.READ, \
        "Only reg reads allowed during done phase!"

      assert xcelreq_msg.addr == 0, \
        "Only reg read to 0 allowed during done phase!"

      # Send xcel response message indicating xcel is done

      s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.READ, result ) )

  # Line tracing

  def line_trace( s ):
    return f"{s.xcel.reqstream}(){s.xcel.respstream}"

