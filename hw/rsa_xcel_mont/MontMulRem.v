//========================================================================
// MontMulRem.v
//========================================================================
// Implements a complete multiplication-remainder operation in
// Montgomery form with a latency-insensitive interface

`ifndef RSA_XCEL_MONT_MONTMULREM_V
`define RSA_XCEL_MONT_MONTMULREM_V

`include "rsa_xcel_mont/AddRedsValRdy.v"

module rsa_xcel_mont_MontMulRem
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

    // 4-state fix; output is 0 if invalid

    logic [31:0] ostream_msg_raw;
    assign ostream_msg = ostream_msg_raw & {32{ostream_val}};

    // Detect when we have a message in flight

    logic have_msg;

    always @( posedge clk ) begin

        if( reset ) have_msg <= 0;

        else if( istream_val & istream_rdy ) have_msg <= 1;

        else if( ostream_val & ostream_rdy ) have_msg <= 0;
    end
    
    // Decompose our inputs

    logic [95:0] istream_msg_reg;

    always @( posedge clk ) begin
        if( reset ) istream_msg_reg <= 96'b0;

        if( istream_val & istream_rdy ) istream_msg_reg <= istream_msg;
    end

    logic [31:0] mul_opa;
    logic [31:0] mul_opb;
    logic [31:0] n;

    assign n       = istream_msg_reg[95:64];
    assign mul_opa = istream_msg_reg[63:32];
    assign mul_opb = istream_msg_reg[31:0];

    // Declare our signal lines for all of our AddReds

    logic [32:0] overall_result;
    logic [32:0] results   [4:0];
    logic        val_bits  [4:0];
    logic        rdy_bits  [4:0];
    logic [7:0]  x_bit_arr [3:0];

    assign results[0]     = 33'b0; // Initial result is 0
    assign overall_result = results[4];

    assign val_bits[0] = istream_val & !have_msg;
    assign ostream_val = val_bits[4];

    assign rdy_bits[4] = ostream_rdy;
    assign istream_rdy = rdy_bits[0] & !have_msg;

    assign x_bit_arr[0] = mul_opa[ 7: 0];
    assign x_bit_arr[1] = mul_opa[15: 8];
    assign x_bit_arr[2] = mul_opa[23:16];
    assign x_bit_arr[3] = mul_opa[31:24];


    // Simply generate the AddReds we need
    // We've determined that we need 4 stages to meet timing

    genvar i;

    generate
        for( i = 0; i < 4; i = i + 1 ) begin: ADDREDS

            rsa_xcel_mont_AddRedsValRdy #(8) addreds_valrdy
            (
                .clk         ( clk           ),
                .reset       ( reset         ),
                
                .x_bits      ( x_bit_arr[i]  ),
                .y           ( mul_opb       ),
                .n           ( n             ),
                .result_in   ( results[i]    ),

                .istream_val ( val_bits[i]   ),
                .istream_rdy ( rdy_bits[i]   ),

                .result_out  ( results[i+1]  ),

                .ostream_val ( val_bits[i+1] ),
                .ostream_rdy ( rdy_bits[i+1] )
            );

        end
    endgenerate

    // Assign overall result

    always @( * ) begin

        if( overall_result > n )
            ostream_msg_raw = overall_result - n;
        
        else
            ostream_msg_raw = overall_result;
    end

endmodule

`endif // RSA_XCEL_MONT_MONTMULREM_V