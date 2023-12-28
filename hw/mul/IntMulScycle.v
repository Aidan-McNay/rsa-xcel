//=========================================================================
// Integer Multiplier Single-Cycle Implementation
//=========================================================================

`ifndef MUL_INT_MUL_SCYCLE_V
`define MUL_INT_MUL_SCYCLE_V

`include "vc/trace.v"
`include "vc/regs.v"

//=========================================================================
// Integer Multiplier Single-Cycle Implementation
//=========================================================================

module mul_IntMulScycle
#(
  parameter nbits = 32
)
(
  input  logic        clk,
  input  logic        reset,

  input  logic        istream_val,
  output logic        istream_rdy,
  input  logic [( 2 * nbits) - 1:0] istream_msg,

  output logic        ostream_val,
  input  logic        ostream_rdy,
  output logic [nbits - 1:0] ostream_msg
);

  // Input registers

  logic val_reg_out;

  vc_EnResetReg#(1) val_reg
  (
    .clk   (clk),
    .reset (reset),
    .d     (istream_val),
    .en    (ostream_rdy),
    .q     (val_reg_out)
  );

  logic [nbits-1:0] a_reg_out;

  vc_EnReg#(nbits) a_reg
  (
    .clk   (clk),
    .reset (reset),
    .d     (istream_msg[ (2 * nbits) - 1:nbits ]),
    .en    (ostream_rdy),
    .q     (a_reg_out)
  );

  logic [nbits-1:0] b_reg_out;

  vc_EnReg#(nbits) b_reg
  (
    .clk   (clk),
    .reset (reset),
    .d     (istream_msg[ nbits - 1 :0 ]),
    .en    (ostream_rdy),
    .q     (b_reg_out)
  );

  logic [nbits - 1:0] product;

  assign istream_rdy = ostream_rdy;
  assign ostream_val = val_reg_out;
  assign product     = a_reg_out * b_reg_out;
  assign ostream_msg = product & {nbits{ostream_val}}; // 4-state sim fix

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%x", istream_msg );

    vc_trace.append_val_rdy_str( trace_str, istream_val, istream_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    if ( val_reg_out ) begin
      vc_trace.append_str( trace_str, "*" );
    end else begin
      vc_trace.append_str( trace_str, " " );
    end

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", ostream_msg );
    vc_trace.append_val_rdy_str( trace_str, ostream_val, ostream_rdy, str );
  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* MUL_INT_MUL_SCYCLE_V */
