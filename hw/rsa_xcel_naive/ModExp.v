//=========================================================================
// ModExp.v
//=========================================================================
// Wrapper for modular exponentiation datapath and control

`ifndef RSA_XCEL_NAIVE_MODEXP_V
`define RSA_XCEL_NAIVE_MODEXP_V

`include "vc/trace.v"

`include "rsa_xcel_naive/ModExpCtrl.v"
`include "rsa_xcel_naive/ModExpDpath.v"

module rsa_xcel_naive_ModExp
(
    input  logic clk,
    input  logic reset,

    // Input stream

    input  logic [95:0] istream_msg,
    input  logic        istream_val,
    output logic        istream_rdy,

    // Output stream

    output logic [31:0] ostream_msg,
    output logic        ostream_val,
    input  logic        ostream_rdy
);

    // Decompose inputs

    logic [31:0] b;
    logic [31:0] e;
    logic [31:0] n;

    assign b = istream_msg[31:0];
    assign e = istream_msg[63:32];
    assign n = istream_msg[95:64];

    // Form output

    logic [31:0] result;
    assign ostream_msg = result;

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

    rsa_xcel_naive_ModExpCtrl ctrl
    (
        .*
    );

    //-------------------------------------------------------
    // Datapath Unit
    //-------------------------------------------------------

    rsa_xcel_naive_ModExpDpath dpath
    (
        .*
    );

    //----------------------------------------------------------------------
    // Line Tracing
    //----------------------------------------------------------------------

    `ifndef SYNTHESIS

    // Localparams from control unit

    localparam IDLE            = 2'd0;
    localparam SEND_MULREM_MSG = 2'd1;
    localparam RECV_MULREM_MSG = 2'd2;
    localparam DONE            = 2'd3;

    // Keep track of state of mulrems

    logic r_mulrem_state;
    logic b_mulrem_state;

    initial begin
        r_mulrem_state = 0;
        b_mulrem_state = 0;
    end

    always @( posedge clk ) begin

        // Handle r_mulrem_state
        if( dpath.r_mulrem_i_val & dpath.r_mulrem_i_rdy ) begin
            r_mulrem_state <= 1;
        end
        else if( dpath.r_mulrem_o_val & dpath.r_mulrem_o_rdy ) begin
            r_mulrem_state <= 0;
        end

        // Handle b_mulrem_state
        if( dpath.b_mulrem_i_val & dpath.b_mulrem_i_rdy ) begin
            b_mulrem_state <= 1;
        end
        else if( dpath.b_mulrem_o_val & dpath.b_mulrem_o_rdy ) begin
            b_mulrem_state <= 0;
        end
    end

    logic [`VC_TRACE_NBITS-1:0] str;
    `VC_TRACE_BEGIN
    begin
        
        // Input Stream
        $sformat( str, "%x", istream_msg );
        vc_trace.append_val_rdy_str( trace_str, istream_val, istream_rdy, str );

        // Internal Signals

        vc_trace.append_str( trace_str, "(" );

        case ( ctrl.state_curr )
            IDLE:            vc_trace.append_str( trace_str, "I" );
            SEND_MULREM_MSG: vc_trace.append_str( trace_str, "S" );
            RECV_MULREM_MSG: vc_trace.append_str( trace_str, "R" );
            DONE:            vc_trace.append_str( trace_str, "D" );
            default:         vc_trace.append_str( trace_str, "?" );
        endcase

        vc_trace.append_str( trace_str, "|" );

        // String for r_mulrem

        if( dpath.r_mulrem_o_val & dpath.r_mulrem_o_rdy ) begin
            // Handing off result
            vc_trace.append_str( trace_str, ">" );
        end
        else if( r_mulrem_state & dpath.r_mulrem_o_val ) begin
            // Waiting to hand off
            vc_trace.append_str( trace_str, "." );
        end
        else if( r_mulrem_state ) begin
            // Computing result
            vc_trace.append_str( trace_str, "*" );
        end
        else begin
            // Not doing anything
            vc_trace.append_str( trace_str, " " );
        end

        vc_trace.append_str( trace_str, "|" );

        // String for b_mulrem

        if( dpath.b_mulrem_o_val & dpath.b_mulrem_o_rdy ) begin
            // Handing off result
            vc_trace.append_str( trace_str, ">" );
        end
        else if( b_mulrem_state & dpath.b_mulrem_o_val ) begin
            // Waiting to hand off
            vc_trace.append_str( trace_str, "." );
        end
        else if( b_mulrem_state ) begin
            // Computing result
            vc_trace.append_str( trace_str, "*" );
        end
        else begin
            // Not doing anything
            vc_trace.append_str( trace_str, " " );
        end

        vc_trace.append_str( trace_str, ")" );

        // Output Stream
        $sformat( str, "%x", ostream_msg );
        vc_trace.append_val_rdy_str( trace_str, ostream_val, ostream_rdy, str );

    end
    `VC_TRACE_END

    `endif /* SYNTHESIS */

endmodule

`endif // RSA_XCEL_NAIVE_MODEXP_V