//=========================================================================
// RSA Xcel Unit RTL Model
//=========================================================================
// RSA modular exponentiation accelerator
//
// Accelerator register interface:
//
//  xr0 : go/done
//  xr1 : base
//  xr2 : exponent
//  xr3 : modulus
//
// Accelerator protocol involves the following steps:
//  1. Write the base via xr1
//  2. Write the exponent via xr2
//  3. Write the modulus via xr3
//  4. Tell accelerator to go by writing xr0
//  5. Wait for accelerator to finish by reading xr0, result will be the
//     result of modular exponentiation
//

`ifndef RSA_XCEL_NAIVE_RSAXCEL_V
`define RSA_XCEL_NAIVE_RSAXCEL_V

`include "vc/trace.v"

`include "rsa_xcel_naive/ModExp.v"
`include "rsa_xcel_naive/XcelAdapter.v"

module rsa_xcel_naive_RSAXcel
(
    input  logic clk,
    input  logic reset,

    input  xcel_req_t    xcel_reqstream_msg,
    input  logic         xcel_reqstream_val,
    output logic         xcel_reqstream_rdy,

    output xcel_resp_t   xcel_respstream_msg,
    output logic         xcel_respstream_val,
    input  logic         xcel_respstream_rdy
);

    // Instantiate Adapter

    logic [95:0] modexp_istream_msg;
    logic        modexp_istream_val;
    logic        modexp_istream_rdy;

    logic [31:0] modexp_ostream_msg;
    logic        modexp_ostream_val;
    logic        modexp_ostream_rdy;

    rsa_xcel_naive_XcelAdapter adapter
    (
        .*
    );

    // Instantiate ModExp unit

    rsa_xcel_naive_ModExp modexp
    (
        .clk   ( clk ),
        .reset ( reset ),

        .istream_msg ( modexp_istream_msg ),
        .istream_val ( modexp_istream_val ),
        .istream_rdy ( modexp_istream_rdy ),

        .ostream_msg ( modexp_ostream_msg ),
        .ostream_val ( modexp_ostream_val ),
        .ostream_rdy ( modexp_ostream_rdy )
    );

    //----------------------------------------------------------------------
    // Line Tracing
    //----------------------------------------------------------------------

    `ifndef SYNTHESIS

    // Resp and Reqstream tracers

    vc_XcelReqMsgTrace xcel_reqstream_msg_trace
    (
        .clk   (clk),
        .reset (reset),
        .val   (xcel_reqstream_val),
        .rdy   (xcel_reqstream_rdy),
        .msg   (xcel_reqstream_msg)
    );

    vc_XcelRespMsgTrace xcel_respstream_msg_trace
    (
        .clk   (clk),
        .reset (reset),
        .val   (xcel_respstream_val),
        .rdy   (xcel_respstream_rdy),
        .msg   (xcel_respstream_msg)
    );

    logic [`VC_TRACE_NBITS-1:0] str;
    `VC_TRACE_BEGIN
    begin
        
        // Input Stream
        xcel_reqstream_msg_trace.line_trace( trace_str );

        vc_trace.append_str( trace_str, "(" );

        modexp.line_trace( trace_str );

        vc_trace.append_str( trace_str, ")" );

        // Output Stream
        xcel_respstream_msg_trace.line_trace( trace_str );

    end
    `VC_TRACE_END

    `endif /* SYNTHESIS */

endmodule

`endif // RSA_XCEL_NAIVE_RSAXCEL_V