#=========================================================================
# ModDiv PyMTL3 Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

class ModDiv( VerilogPlaceholder, Component ):
  def construct( s ):
    s.istream = IStreamIfc( mk_bits( 65 ) )
    s.ostream = OStreamIfc( Bits32 )
