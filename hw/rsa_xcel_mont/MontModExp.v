//=========================================================================
// MontModExp.v
//=========================================================================
// Tie together our converters and multiplier to form the overall modular
// exponentiation unit

`ifndef RSA_XCEL_MONT_MONTMODEXP_V
`define RSA_XCEL_MONT_MONTMODEXP_V

`include "vc/trace.v"

`include "rsa_xcel_mont/MontConvertIn.v"
`include "rsa_xcel_mont/MontConvertOut.v"
`include "rsa_xcel_mont/MontModExpMul.v"

module rsa_xcel_mont_MontModExp
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

    // Declare our main multiplier

    logic [127:0] modexpmul_input;
    logic  [63:0] modexpmul_output;

    logic         modexpmul_i_val;
    logic         modexpmul_i_rdy;

    logic         modexpmul_o_val;
    logic         modexpmul_o_rdy;
    

    rsa_xcel_mont_MontModExpMul modexpmul
    (
        .clk         ( clk ),
        .reset       ( reset ),

        // Input stream

        .istream_msg ( modexpmul_input ),
        .istream_val ( modexpmul_i_val ),
        .istream_rdy ( modexpmul_i_rdy ),

        // Output stream

        .ostream_msg ( modexpmul_output ),
        .ostream_val ( modexpmul_o_val ),
        .ostream_rdy ( modexpmul_o_rdy )
    );

    // Declare our ConvertIn to convert the input stream

    rsa_xcel_mont_MontConvertIn convert_in
    (
        .clk         ( clk ),
        .reset       ( reset ),

        // Input stream

        .istream_msg ( istream_msg ),
        .istream_val ( istream_val ),
        .istream_rdy ( istream_rdy ),

        // Output stream

        .ostream_msg ( modexpmul_input ),
        .ostream_val ( modexpmul_i_val ),
        .ostream_rdy ( modexpmul_i_rdy )
    );

    // Declare our ConvertOut to convert the output stream

    rsa_xcel_mont_MontConvertOut convert_out
    (
        .clk         ( clk ),
        .reset       ( reset ),

        // Input stream

        .istream_msg ( modexpmul_output ),
        .istream_val ( modexpmul_o_val  ),
        .istream_rdy ( modexpmul_o_rdy  ),

        // Output stream

        .ostream_msg ( ostream_msg ),
        .ostream_val ( ostream_val ),
        .ostream_rdy ( ostream_rdy )
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

    // Keep track of state of mulrems and conversion units

    logic r_mulrem_state;
    logic b_mulrem_state;
    logic conv_in_state;
    logic conv_out_state;

    initial begin
        r_mulrem_state = 0;
        b_mulrem_state = 0;
        conv_in_state  = 0;
        conv_out_state = 0;
    end

    always @( posedge clk ) begin

        // Handle r_mulrem_state
        if( modexpmul.dpath.r_mulrem_i_val & modexpmul.dpath.r_mulrem_i_rdy ) begin
            r_mulrem_state <= 1;
        end
        else if( modexpmul.dpath.r_mulrem_o_val & modexpmul.dpath.r_mulrem_o_rdy ) begin
            r_mulrem_state <= 0;
        end

        // Handle b_mulrem_state
        if( modexpmul.dpath.b_mulrem_i_val & modexpmul.dpath.b_mulrem_i_rdy ) begin
            b_mulrem_state <= 1;
        end
        else if( modexpmul.dpath.b_mulrem_o_val & modexpmul.dpath.b_mulrem_o_rdy ) begin
            b_mulrem_state <= 0;
        end

        // Handle conv_in_state
        if( istream_val & istream_rdy ) begin // Control signals for convert_in input
            conv_in_state <= 1;
        end
        else if( modexpmul_i_val & modexpmul_i_rdy ) begin // Control signals for convert_in output
            conv_in_state <= 0;
        end

        // Handle conv_out_state
        if( modexpmul_o_val & modexpmul_o_rdy ) begin // Control signals for convert_out input
            conv_out_state <= 1;
        end
        else if( ostream_val & ostream_rdy ) begin // Control signals for convert_out output
            conv_out_state <= 0;
        end
    end

    logic [`VC_TRACE_NBITS-1:0] str;
    `VC_TRACE_BEGIN
    begin
        
        // Input Stream
        $sformat( str, "%x", istream_msg );
        vc_trace.append_val_rdy_str( trace_str, istream_val, istream_rdy, str );

        //---------------------- Convert In ----------------------

        vc_trace.append_str( trace_str, "(" );

        if( modexpmul_i_val & modexpmul_i_rdy ) begin 
            // Handing off result
            vc_trace.append_str( trace_str, ">" );
        end
        else if( modexpmul_i_val ) begin
            // Waiting to hand off response
            vc_trace.append_str( trace_str, "." );
        end
        else if( conv_in_state ) begin
            // Calculating result
            vc_trace.append_str( trace_str, "*" );
        end
        else begin
            // Not doing anything
            vc_trace.append_str( trace_str, " " );
        end

        vc_trace.append_str( trace_str, ")" );
        
        //---------------------- ModExpMul ----------------------

        vc_trace.append_str( trace_str, "(" );

        case ( modexpmul.ctrl.state_curr )
            IDLE:            vc_trace.append_str( trace_str, "I" );
            SEND_MULREM_MSG: vc_trace.append_str( trace_str, "S" );
            RECV_MULREM_MSG: vc_trace.append_str( trace_str, "R" );
            DONE:            vc_trace.append_str( trace_str, "D" );
            default:         vc_trace.append_str( trace_str, "?" );
        endcase

        vc_trace.append_str( trace_str, "|" );

        // String for r_mulrem

        if( modexpmul.dpath.r_mulrem_o_val & modexpmul.dpath.r_mulrem_o_rdy ) begin
            // Handing off result
            vc_trace.append_str( trace_str, ">" );
        end
        else if( r_mulrem_state & modexpmul.dpath.r_mulrem_o_val ) begin
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

        if( modexpmul.dpath.b_mulrem_o_val & modexpmul.dpath.b_mulrem_o_rdy ) begin
            // Handing off result
            vc_trace.append_str( trace_str, ">" );
        end
        else if( b_mulrem_state & modexpmul.dpath.b_mulrem_o_val ) begin
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

        //---------------------- Convert Out ----------------------

        vc_trace.append_str( trace_str, "(" );

        if( ostream_val & ostream_rdy ) begin 
            // Handing off result
            vc_trace.append_str( trace_str, ">" );
        end
        else if( ostream_val ) begin
            // Waiting to hand off response
            vc_trace.append_str( trace_str, "." );
        end
        else if( conv_out_state ) begin
            // Calculating result
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

`endif // RSA_XCEL_MONT_MONTMODEXP_V