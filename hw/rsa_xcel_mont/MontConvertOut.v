//========================================================================
// MontConvertOut.v
//========================================================================
// Converts our outputs out of Montgomery Form

`ifndef RSA_XCEL_MONT_MONTCONVERTOUT_V
`define RSA_XCEL_MONT_MONTCONVERTOUT_V

`include "rsa_xcel_mont/MontMulRem.v"

module rsa_xcel_mont_MontConvertOut
(
    input  logic clk,
    input  logic reset,

    // Input stream

    input  logic [63:0] istream_msg,
    input  logic        istream_val,
    output logic        istream_rdy,

    // Output stream

    output logic [31:0] ostream_msg,
    output logic        ostream_val,
    input  logic        ostream_rdy
);

    // Decompose inputs

    logic [31:0] result;
    logic [31:0] n;

    assign result = istream_msg[31:0];
    assign n      = istream_msg[63:32];

    // Declare our MontMulRem

    rsa_xcel_mont_MontMulRem montmulrem
    (
        .clk         ( clk ),
        .reset       ( reset ),

        .istream_msg ( { n, result, 32'b1 } ),
        .istream_val ( istream_val ),
        .istream_rdy ( istream_rdy ),

        .ostream_msg ( ostream_msg ),
        .ostream_val ( ostream_val ),
        .ostream_rdy ( ostream_rdy )
    );

endmodule

`endif // RSA_XCEL_MONT_MONTCONVERTOUT