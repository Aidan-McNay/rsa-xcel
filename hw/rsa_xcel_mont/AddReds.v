//========================================================================
// AddReds.v
//========================================================================
// Strings together many add-reduce steps

`ifndef RSA_XCEL_MONT_ADDREDS_V
`define RSA_XCEL_MONT_ADDREDS_V

`include "rsa_xcel_mont/AddRed.v"

module rsa_xcel_mont_AddReds
#(
    parameter p_nsteps = 32
)(
    // Inputs for the step

    input  logic [p_nsteps - 1:0] x_bits,
    input  logic [31:0]           y,
    input  logic [31:0]           n,
    input  logic [32:0]           result_in,

    // Outputs for the step

    output logic [32:0] result_out
);

    // Create an array for the intermediate results

    logic [32:0] results [p_nsteps:0];
    
    assign results[0] = result_in;
    assign result_out = results[p_nsteps];

    // Generate our steps

    genvar i;

    generate
        for( i = 0; i < p_nsteps; i = i + 1 ) begin: ADDREDSTEPS

            rsa_xcel_mont_AddRed addred
            (
                .x_bit      ( x_bits[i]    ),
                .y          ( y            ),
                .n          ( n            ),
                .result_in  ( results[i]   ),

                .result_out ( results[i+1] )
            );

        end
    endgenerate

endmodule

`endif // RSA_XCEL_MONT_ADDREDS_V