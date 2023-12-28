//========================================================================
// ModExpCtrl.v
//========================================================================
// Implements the modular exponentiation control unit

`ifndef RSA_XCEL_NAIVE_MODEXPCTRL_V
`define RSA_XCEL_NAIVE_MODEXPCTRL_V

module rsa_xcel_naive_ModExpCtrl
(
    input  logic clk,
    input  logic reset,

    // Input control signals

    input  logic istream_val,
    output logic istream_rdy,

    // Output control signals

    output logic ostream_val,
    input  logic ostream_rdy,

    // Control signals ( ctrl -> dpath )

    output logic e_mux_sel,
    output logic r_mux_sel,
    output logic b_mux_sel,

    output logic e_reg_en,
    output logic r_reg_en,
    output logic b_reg_en,
    output logic n_reg_en,

    output logic r_mulrem_i_val,
    output logic r_mulrem_o_rdy,

    output logic b_mulrem_i_val,
    output logic b_mulrem_o_rdy,

    // Status signals ( dpath -> ctrl )

    input  logic [31:0] e_reg_out,

    input  logic        r_mulrem_i_rdy,
    input  logic        r_mulrem_o_val,

    input  logic        b_mulrem_i_rdy,
    input  logic        b_mulrem_o_val
);

    //-------------------------------------------------------
    // Define FSM states
    //-------------------------------------------------------

    localparam IDLE            = 2'd0;
    localparam SEND_MULREM_MSG = 2'd1;
    localparam RECV_MULREM_MSG = 2'd2;
    localparam DONE            = 2'd3;

    //-------------------------------------------------------
    // Define FSM transitions
    //-------------------------------------------------------

    logic [1:0] state_curr;
    logic [1:0] state_next;

    logic mulrems_i_rdy;
    logic mulrems_o_val;

    always @( posedge clk ) begin
        state_curr <= state_next;
    end

    always @( * ) begin

        // Default
        state_next = state_curr;

        if( reset ) state_next = IDLE;

        else if( state_curr == IDLE ) begin
            
            if( istream_val ) state_next = SEND_MULREM_MSG;

        end

        else if( state_curr == SEND_MULREM_MSG ) begin

            if( mulrems_i_rdy ) begin
                state_next = RECV_MULREM_MSG;
            end

        end

        else if( state_curr == RECV_MULREM_MSG ) begin

            if( mulrems_o_val ) begin

                if( ( e_reg_out >> 1 ) == 0 ) state_next = DONE;

                else state_next = SEND_MULREM_MSG;

            end

        end

        else if( state_curr == DONE ) begin

            if( ostream_rdy ) state_next = IDLE;

        end
    end

    //-------------------------------------------------------
    // Define outputs based on FSM states
    //-------------------------------------------------------

    // Overall control signals

    assign istream_rdy = ( state_curr == IDLE );
    assign ostream_val = ( state_curr == DONE );

    // Muxes and n_reg only take in external output in IDLE

    always @( * ) begin

        if( state_curr == IDLE ) begin
            e_mux_sel = 0;
            r_mux_sel = 0;
            b_mux_sel = 0;

            n_reg_en = 1;
        end

        else begin
            e_mux_sel = 1;
            r_mux_sel = 1;
            b_mux_sel = 1;

            n_reg_en = 0;
        end
    end

    // Only enable data registers during IDLE, as well as
    // once the mulrems are done in RECV_MULREM_MSG

    logic e_lsb;
    assign e_lsb = e_reg_out[0];

    always @( * ) begin

        if( state_curr == IDLE ) begin
            e_reg_en = 1;
            b_reg_en = 1;
            r_reg_en = 1;
        end

        else if( ( ( state_curr == RECV_MULREM_MSG ) & mulrems_o_val ) ) begin
            e_reg_en = 1;
            b_reg_en = 1;

            // Only register r when the lsb of e is 1
            if( e_lsb ) begin
                r_reg_en = 1;
            end else begin
                r_reg_en = 0;
            end
        end

        else begin
            e_reg_en = 0;
            b_reg_en = 0;
            r_reg_en = 0;
        end

    end

    // Lastly, we define the val and rdy signals for the mulrems.

    // We have to be careful doing this, as since we want both to happen
    // at the same time, we have to base the input val on the rdy, and
    // the output rdy on the val. However, since only the top level bases
    // one control signal on the other, it should be ok

    always @( * ) begin

        if( e_lsb == 1 ) begin
            // Need to use both mulrems
            mulrems_i_rdy = ( b_mulrem_i_rdy & r_mulrem_i_rdy );
            mulrems_o_val = ( b_mulrem_o_val & r_mulrem_o_val );
        end

        else begin
            // Only need to consider the b mulrem
            mulrems_i_rdy = b_mulrem_i_rdy;
            mulrems_o_val = b_mulrem_o_val;
        end
    end

    // Assign istream_val and ostream_rdy for the mulrems
    logic mulrems_i_val;
    logic mulrems_o_rdy;

    always @( * ) begin

        if( state_curr == SEND_MULREM_MSG ) begin
            mulrems_i_val = mulrems_i_rdy;
            mulrems_o_rdy = 0;
        end

        else if( state_curr == RECV_MULREM_MSG ) begin
            mulrems_i_val = 0;
            mulrems_o_rdy = mulrems_o_val;
        end

        else begin
            mulrems_i_val = 0;
            mulrems_o_rdy = 0;
        end
    end

    assign r_mulrem_i_val = ( e_lsb ) ? mulrems_i_val : 1'b0;
    assign b_mulrem_i_val = mulrems_i_val;

    assign r_mulrem_o_rdy = ( e_lsb ) ? mulrems_o_rdy : 1'b0;
    assign b_mulrem_o_rdy = mulrems_o_rdy;

endmodule

`endif // RSA_XCEL_NAIVE_MODEXPCTRL_V