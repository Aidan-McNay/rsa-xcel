//========================================================================
// AddRem.v
//========================================================================
// Implements a add-reduce step for use in MulRem

`ifndef RSA_XCEL_MONT_ADDRED_V
`define RSA_XCEL_MONT_ADDRED_V

module rsa_xcel_mont_AddRed
(
    // Inputs for the step

    input  logic        x_bit,
    input  logic [31:0] y,
    input  logic [31:0] n,
    input  logic [32:0] result_in,

    // Outputs for the step

    output logic [32:0] result_out
);

    // Compute factor from y to add, if any

    logic [31:0] y_factor;
    assign y_factor = { 32{ x_bit } } & y;

    // Compute factor from n, to add to y in the case
    // that we need to add both y and n to the result

    logic [32:0] y_n_factor;
    assign y_n_factor = { 1'b0, n } + { 1'b0, y_factor };

    // Mux the two factors based on the LSB of 
    // result_in + y_factor, to determine if we need to
    // add n
    //
    // This can be done with sum_lsb, the LSB of
    // result_in + y_factor, which can be computed in 
    // advance

    logic sum_lsb;
    assign sum_lsb = result_in[0] ^ ( x_bit & y[0] );

    logic [32:0] factor_to_add;
    assign factor_to_add = ( sum_lsb ) ? y_n_factor : { 1'b0, y_factor };

    // Add the factor to our running result

    logic [33:0] temp_result;
    assign temp_result = { 1'b0, result_in } + { 1'b0, factor_to_add };

    // Assign our result to temp_result divided by 2
    assign result_out = temp_result >> 1;

endmodule

`endif // RSA_XCEL_MONT_ADDRED_V