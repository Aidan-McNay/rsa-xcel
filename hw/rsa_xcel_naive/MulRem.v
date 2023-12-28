//========================================================================
// MulRem.v
//========================================================================
// Implements a multiplication-remainder operation

`ifndef RSA_XCEL_NAIVE_MULREM_V
`define RSA_XCEL_NAIVE_MULREM_V

`include "vc/regs.v"

`include "mul/IntMulScycle.v"
`include "div/ModDiv.v"

module rsa_xcel_naive_MulRem
(
    input  logic clk,
    input  logic reset,

    input  logic [95:0] istream_msg,
    input  logic        istream_val,
    output logic        istream_rdy,

    output logic [31:0] ostream_msg,
    output logic        ostream_val,
    input  logic        ostream_rdy
);

    // Separate inputs into their values;

    logic [31:0] mul_opa;
    logic [31:0] mul_opb;
    logic [31:0] n;

    assign n       = istream_msg[95:64];
    assign mul_opa = istream_msg[63:32];
    assign mul_opb = istream_msg[31:0];

    // Register n for each new message

    logic [31:0] n_reg_out;

    vc_EnResetReg#( 32, 0 ) n_reg
    (
        .clk   ( clk ),
        .reset ( reset ),

        .q     ( n_reg_out ),
        .d     ( n ),
        .en    ( istream_val & istream_rdy )
    );

    // Multiplier

    logic        mul_rem_val;
    logic        mul_rem_rdy;
    logic [63:0] mul_out;

    mul_IntMulScycle #( 64 ) imul
    (
      .clk         (clk),
      .reset       (reset),

      .istream_val (istream_val),
      .istream_rdy (istream_rdy),
      .istream_msg ({ 32'b0, mul_opa, 32'b0, mul_opb }),

      .ostream_val (mul_rem_val),
      .ostream_rdy (mul_rem_rdy),
      .ostream_msg (mul_out)
    );

    // Remainder

    logic [63:0] div_out;

    div_ModDiv #( 64 ) div_rem
    (
      .clk         (clk),
      .reset       (reset),

      .istream_val (mul_rem_val),
      .istream_rdy (mul_rem_rdy),
      .istream_msg ({ 1'b1, mul_out, { 32'b0, n_reg_out } }),

      .ostream_val (ostream_val),
      .ostream_rdy (ostream_rdy),
      .ostream_msg (div_out)
    );

    assign ostream_msg = div_out[31:0];

endmodule

`endif // RSA_XCEL_NAIVE_MULREM_V