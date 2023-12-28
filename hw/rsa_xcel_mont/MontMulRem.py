#=========================================================================
# MontMulRem PyMTL3 Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

class MontMulRem( VerilogPlaceholder, Component ):
  def construct( s ):
    s.istream = IStreamIfc( mk_bits( 96 ) )
    s.ostream = OStreamIfc( Bits32 )

    s.set_metadata( VerilogTranslationPass.explicit_module_name,
                    'MontMulRem' )