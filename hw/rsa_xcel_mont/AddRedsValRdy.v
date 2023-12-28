//========================================================================
// AddRedsValRdy.v
//========================================================================
// A thin latency-insensitive wrapper around AddReds.v

`ifndef RSA_XCEL_MONT_ADDREDSVALRDY_V
`define RSA_XCEL_MONT_ADDREDSVALRDY_V

`include "rsa_xcel_mont/AddReds.v"

module rsa_xcel_mont_AddRedsValRdy
#(
    parameter p_nsteps = 32
)(
    input  logic                  clk,
    input  logic                  reset,
    
    // Inputs for the step

    input  logic [p_nsteps - 1:0] x_bits,
    input  logic [31:0]           y,
    input  logic [31:0]           n,
    input  logic [32:0]           result_in,

    // Input Latency-Insensitive Interface

    input  logic                  istream_val,
    output logic                  istream_rdy,

    // Outputs for the step

    output logic [32:0]           result_out,

    // Output Latency-Insensitive Interface

    output logic                  ostream_val,
    input  logic                  ostream_rdy
);

    // Keep track of whether we have a valid message

    logic is_valid;

    always @( posedge clk ) begin

        if( reset ) is_valid <= 0;

        // When we have a valid transaction
        else if( istream_val & istream_rdy ) is_valid <= 1;

        // When we get rid of a valid message and don't replace
        else if( ostream_val & ostream_rdy ) is_valid <= 0;

    end

    assign ostream_val = is_valid;

    // Only not ready when we have a valid message and the ostream can't take it
    assign istream_rdy = ( !is_valid | ostream_rdy );

    // Register our inputs

    logic [32:0]           result_in_reg;

    always @( posedge clk ) begin

        if( reset ) begin
            result_in_reg <= 0;
        end

        else if( istream_val & istream_rdy ) begin
            result_in_reg <= result_in;
        end
    end

    // Our main AddReds module

    rsa_xcel_mont_AddReds #(p_nsteps) addreds
    (
        .x_bits     ( x_bits        ),
        .y          ( y             ),
        .n          ( n             ),
        .result_in  ( result_in_reg ),
        .result_out ( result_out    )
    );

endmodule

`endif // RSA_XCEL_MONT_ADDREDSVALRDY_V