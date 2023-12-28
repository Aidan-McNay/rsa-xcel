#=========================================================================
# MontConvertOut PyMTL3 Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

class MontConvertOut( VerilogPlaceholder, Component ):
  def construct( s ):
    s.istream = IStreamIfc( Bits64 )
    s.ostream = OStreamIfc( Bits32 )
