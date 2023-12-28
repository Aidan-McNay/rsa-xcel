//========================================================================
// MontConvertIn.v
//========================================================================
// Converts our inputs into Montgomery Form

`ifndef RSA_XCEL_MONT_MONTCONVERTIN_V
`define RSA_XCEL_MONT_MONTCONVERTIN_V

`include "vc/regs.v"

`include "div/ModDiv.v"
`include "rsa_xcel_mont/MontMulRem.v"

module rsa_xcel_mont_MontConvertIn
(
    input  logic clk,
    input  logic reset,

    // Input stream

    input  logic [95:0]  istream_msg,
    input  logic         istream_val,
    output logic         istream_rdy,

    // Output stream

    output logic [127:0] ostream_msg,
    output logic         ostream_val,
    input  logic         ostream_rdy
);

    // Decompose inputs

    logic [31:0] b_in;
    logic [31:0] e_in;
    logic [31:0] n_in;

    assign b_in = istream_msg[31: 0];
    assign e_in = istream_msg[63:32];
    assign n_in = istream_msg[95:64];

    // Declare remainder unit for calculating R^2 mod n

    localparam R_2 = 65'h10000000000000000;

    logic [64:0] rem_result;
    logic        rem_ostream_val;
    logic        rem_ostream_rdy;

    div_ModDiv #( 65 ) div_rem
    (
      .clk         ( clk ),
      .reset       ( reset ),

      .istream_val ( istream_val ),
      .istream_rdy ( istream_rdy ),
      .istream_msg ( { 1'b1, R_2, { 33'b0, n_in } } ),

      .ostream_val ( rem_ostream_val ),
      .ostream_rdy ( rem_ostream_rdy ),
      .ostream_msg ( rem_result )
    );

    logic [31:0] R_2_mod_n;
    assign R_2_mod_n = rem_result[31:0];

    // Register our other inputs, to keep track of them
    // with our overall message

    logic [31:0] e_reg1;
    logic [31:0] n_reg1;
    logic [31:0] b_reg;

    always @( posedge clk ) begin
        if( reset ) begin
            e_reg1 <= 0;
            n_reg1 <= 0;
            b_reg  <= 0;
        end

        else if( istream_val & istream_rdy ) begin
            e_reg1 <= e_in;
            n_reg1 <= n_in;
            b_reg  <= b_in;
        end
    end

    // Declare our MontMulRems for converting into Montgomery Form

    logic montmulrem_i_val;
    logic r_montmulrem_i_rdy;
    logic b_montmulrem_i_rdy;

    logic montmulrem_o_rdy;
    logic r_montmulrem_o_val;
    logic b_montmulrem_o_val;

    logic [31:0] r_converted;
    logic [31:0] b_converted;

    rsa_xcel_mont_MontMulRem r_montmulrem
    (
        .clk         ( clk ),
        .reset       ( reset ),

        .istream_msg ( { n_reg1, 32'b1, R_2_mod_n } ),
        .istream_val ( montmulrem_i_val ),
        .istream_rdy ( r_montmulrem_i_rdy ),

        .ostream_msg ( r_converted ),
        .ostream_val ( r_montmulrem_o_val ),
        .ostream_rdy ( montmulrem_o_rdy )
    );

    rsa_xcel_mont_MontMulRem b_montmulrem
    (
        .clk         ( clk ),
        .reset       ( reset ),

        .istream_msg ( { n_reg1, b_reg, R_2_mod_n } ),
        .istream_val ( montmulrem_i_val ),
        .istream_rdy ( b_montmulrem_i_rdy ),

        .ostream_msg ( b_converted ),
        .ostream_val ( b_montmulrem_o_val ),
        .ostream_rdy ( montmulrem_o_rdy )
    );

    // For our val/rdy logic, since we have 2 MontMulRems, we have to be
    // careful to only have a transaction when both can do it. This results
    // in one control signal being based on the other, but since the control
    // signals inside our MontMulRems are independent, we should be ok

    // Handle MontMulRem input val/rdy logic

    assign rem_ostream_rdy  = r_montmulrem_i_rdy & b_montmulrem_i_rdy;
    assign montmulrem_i_val = rem_ostream_val & rem_ostream_rdy;

    // Handle MontMulRem output val/rdy logic

    assign ostream_val      = r_montmulrem_o_val & b_montmulrem_o_val;
    assign montmulrem_o_rdy = ostream_val & ostream_rdy;

    // Register our other values, to keep track of them
    // with our overall message

    logic [31:0] n_reg2;
    logic [31:0] e_reg2;

    always @( posedge clk ) begin
        if( reset ) begin
            e_reg2 <= 0;
            n_reg2 <= 0;
        end

        else if( montmulrem_i_val ) begin // Only high when a transaction is about to happen
            e_reg2 <= e_reg1;
            n_reg2 <= n_reg1;
        end
    end

    // Form our output message

    assign ostream_msg[ 31: 0] = b_converted;
    assign ostream_msg[ 63:32] = e_reg2;
    assign ostream_msg[ 95:64] = n_reg2;
    assign ostream_msg[127:96] = r_converted;

endmodule

`endif // RSA_XCEL_MONT_MONTCONVERTIN_V