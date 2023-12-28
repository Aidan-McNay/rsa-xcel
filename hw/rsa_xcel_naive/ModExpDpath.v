//========================================================================
// ModExpDpath.v
//========================================================================
// Implements the modular exponentiation datapath

`ifndef RSA_XCEL_NAIVE_MODEXPDPATH_V
`define RSA_XCEL_NAIVE_MODEXPDPATH_V

`include "vc/muxes.v"
`include "vc/regs.v"
`include "rsa_xcel_naive/MulRem.v"

module rsa_xcel_naive_ModExpDpath
(
    input  logic clk,
    input  logic reset,

    // Input data

    input  logic [31:0] b,
    input  logic [31:0] e,
    input  logic [31:0] n,

    // Output data

    output logic [31:0] result,

    // Control signals ( ctrl -> dpath )

    input  logic e_mux_sel,
    input  logic r_mux_sel,
    input  logic b_mux_sel,

    input  logic e_reg_en,
    input  logic r_reg_en,
    input  logic b_reg_en,
    input  logic n_reg_en,

    input  logic r_mulrem_i_val,
    input  logic r_mulrem_o_rdy,

    input  logic b_mulrem_i_val,
    input  logic b_mulrem_o_rdy,

    // Status signals ( dpath -> ctrl )

    output logic [31:0] e_reg_out,

    output logic        r_mulrem_i_rdy,
    output logic        r_mulrem_o_val,

    output logic        b_mulrem_i_rdy,
    output logic        b_mulrem_o_val
);

    // Mux our inputs

    logic [31:0] e_mux_out;
    logic [31:0] r_mux_out;
    logic [31:0] b_mux_out;

    logic [31:0] e_shift_out;
    logic [31:0] r_mulrem_out;
    logic [31:0] b_mulrem_out;

    vc_Mux2 #( 32 ) e_mux
    (
        .in0 ( e ),
        .in1 ( e_shift_out ),
        .sel ( e_mux_sel ),
        .out ( e_mux_out )
    );

    vc_Mux2 #( 32 ) r_mux
    (
        .in0 ( 32'b1 ),
        .in1 ( r_mulrem_out ),
        .sel ( r_mux_sel ),
        .out ( r_mux_out )
    );

    vc_Mux2 #( 32 ) b_mux
    (
        .in0 ( b ),
        .in1 ( b_mulrem_out ),
        .sel ( b_mux_sel ),
        .out ( b_mux_out )
    );

    // Register the output of our muxes, as well as n

    logic [31:0] n_reg_out;
    logic [31:0] b_reg_out;
    logic [31:0] r_reg_out;

    vc_EnResetReg#( 32, 0 ) e_reg
    (
        .clk   ( clk ),
        .reset ( reset ),
        .q     ( e_reg_out ),
        .d     ( e_mux_out ),
        .en    ( e_reg_en )
    );

    vc_EnResetReg#( 32, 0 ) r_reg
    (
        .clk   ( clk ),
        .reset ( reset ),
        .q     ( r_reg_out ),
        .d     ( r_mux_out ),
        .en    ( r_reg_en )
    );

    vc_EnResetReg#( 32, 0 ) b_reg
    (
        .clk   ( clk ),
        .reset ( reset ),
        .q     ( b_reg_out ),
        .d     ( b_mux_out ),
        .en    ( b_reg_en )
    );

    vc_EnResetReg#( 32, 0 ) n_reg
    (
        .clk   ( clk ),
        .reset ( reset ),
        .q     ( n_reg_out ),
        .d     ( n ),
        .en    ( n_reg_en )
    );

    // Shift our value for e

    assign e_shift_out = ( e_reg_out >> 1 );

    // Use MulRem units for r and b

    logic [95:0] r_mulrem_istream_msg;
    logic [95:0] b_mulrem_istream_msg;

    assign r_mulrem_istream_msg = { n_reg_out, r_reg_out, b_reg_out };
    assign b_mulrem_istream_msg = { n_reg_out, b_reg_out, b_reg_out };

    rsa_xcel_naive_MulRem r_mulrem
    (
        .clk         ( clk ),
        .reset       ( reset ),

        // Input stream interface

        .istream_msg ( r_mulrem_istream_msg ),
        .istream_val ( r_mulrem_i_val ),
        .istream_rdy ( r_mulrem_i_rdy ),

        // Output stream interface

        .ostream_msg ( r_mulrem_out ),
        .ostream_val ( r_mulrem_o_val ),
        .ostream_rdy ( r_mulrem_o_rdy )
    );

    rsa_xcel_naive_MulRem b_mulrem
    (
        .clk         ( clk ),
        .reset       ( reset ),

        // Input stream interface

        .istream_msg ( b_mulrem_istream_msg ),
        .istream_val ( b_mulrem_i_val ),
        .istream_rdy ( b_mulrem_i_rdy ),

        // Output stream interface

        .ostream_msg ( b_mulrem_out ),
        .ostream_val ( b_mulrem_o_val ),
        .ostream_rdy ( b_mulrem_o_rdy )
    );

    // Assign our output value to be the result at the endo of computations

    assign result = r_reg_out;

endmodule

`endif // RSA_XCEL_NAIVE_MODEXPDPATH_V