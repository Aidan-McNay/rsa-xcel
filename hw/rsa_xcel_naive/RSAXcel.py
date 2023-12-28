#=========================================================================
# RSA Xcel Unit PyMTL Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.xcel.ifcs import XcelResponderIfc
from pymtl3.stdlib.xcel      import mk_xcel_msg

class RSAXcel( VerilogPlaceholder, Component ):

  def construct( s ):
    XcelReqMsg, XcelRespMsg = mk_xcel_msg( 5, 32 )

    s.xcel = XcelResponderIfc( XcelReqMsg, XcelRespMsg )

    s.set_metadata( VerilogTranslationPass.explicit_module_name,
                    'RSAXcel' )

