//========================================================================
// MontModExpMul.v
//========================================================================
// Implements the multiplication aspects of modular exponentiation in
// Montgomery form (but not the conversion in and out)

`ifndef RSA_XCEL_MONT_MONTMODEXPMUL_V
`define RSA_XCEL_MONT_MONTMODEXPMUL_V

`include "rsa_xcel_mont/MontModExpMulCtrl.v"
`include "rsa_xcel_mont/MontModExpMulDpath.v"

module rsa_xcel_mont_MontModExpMul
(
    input  logic clk,
    input  logic reset,

    // Input stream

    input  logic [127:0] istream_msg,
    input  logic         istream_val,
    output logic         istream_rdy,

    // Output stream

    output logic [63:0]  ostream_msg,
    output logic         ostream_val,
    input  logic         ostream_rdy
);

    // Decompose inputs

    logic [31:0] b;
    logic [31:0] e;
    logic [31:0] n;
    logic [31:0] result_in;

    assign b         = istream_msg[ 31: 0];
    assign e         = istream_msg[ 63:32];
    assign n         = istream_msg[ 95:64];
    assign result_in = istream_msg[127:96];

    // Form output

    logic [31:0] result;
    logic [31:0] n_out;
    assign ostream_msg = { n_out, result };

    // Control signal declarations

    logic e_mux_sel;
    logic r_mux_sel;
    logic b_mux_sel;

    logic e_reg_en;
    logic r_reg_en;
    logic b_reg_en;
    logic n_reg_en;

    logic r_mulrem_i_val;
    logic r_mulrem_o_rdy;

    logic b_mulrem_i_val;
    logic b_mulrem_o_rdy;

    // Status signal declarations

    logic [31:0] e_reg_out;

    logic        r_mulrem_i_rdy;
    logic        r_mulrem_o_val;

    logic        b_mulrem_i_rdy;
    logic        b_mulrem_o_val;

    //-------------------------------------------------------
    // Control Unit
    //-------------------------------------------------------

    rsa_xcel_mont_MontModExpMulCtrl ctrl
    (
        .*
    );

    //-------------------------------------------------------
    // Datapath Unit
    //-------------------------------------------------------

    rsa_xcel_mont_MontModExpMulDpath dpath
    (
        .*
    );

endmodule

`endif // RSA_XCEL_MONT_MONTMODEXPMUL_V