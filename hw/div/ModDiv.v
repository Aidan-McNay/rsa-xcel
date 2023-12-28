//========================================================================
// ModDiv.v
//========================================================================
// Implements division or remainder operations via modular division

`ifndef DIV_MOD_DIV_V
`define DIV_MOD_DIV_V

module div_ModDiv 
#(
  parameter nbits = 32
)(
    input  logic        clk,
    input  logic        reset,
    
    input  logic [( 2 * nbits):0]     istream_msg, // Two 32-bit operands, plus the msg_sel
    input  logic                      istream_val,
    output logic                      istream_rdy,

    output logic [nbits - 1:0]        ostream_msg,
    output logic                      ostream_val,
    input  logic                      ostream_rdy
);

    // Performs opa/opb using modular division with a 
    // latency-insensitive interface

    // NOTE: Division by 0 is undefined behavior
    // (in reality, the module will just never return a message)

    // Unpack operands

    logic [nbits - 1:0] opa;
    logic [nbits - 1:0] opb;
    logic               msg_sel; // 0 for division, 1 for remainder

    assign opa     = istream_msg[(2 * nbits) - 1:nbits];
    assign opb     = istream_msg[nbits - 1:0];
    assign msg_sel = istream_msg[(2 * nbits)];


    // Define FSM states

    localparam IDLE      = 2'd0;
    localparam SHIFT_OPB = 2'd1;
    localparam CALC      = 2'd2;
    localparam DONE      = 2'd3;

    // Define datapath nets

    logic  [nbits - 1:0] opa_reg;
    logic  [nbits - 1:0] opb_reg;
    logic  [nbits - 1:0] opb_value;

    logic [nbits - 1:0] opb_reg_sl;
    assign opb_reg_sl = opb_reg << 1;

    //--------------------Control Logic--------------------

    // Define FSM transitions

    logic  [1:0] state_curr;
    logic  [1:0] state_next;

    always @( posedge clk ) begin
        state_curr <= state_next;
    end

    always @( * ) begin
        
        if( reset )
            state_next = IDLE;

        else if( state_curr == IDLE ) begin
            if( istream_val ) begin

                if( opb > opa ) // Early exit
                    state_next = DONE;

                else if( opb[nbits - 1] == 1 ) // Already shifted left
                    state_next = CALC;

                else state_next = SHIFT_OPB;
            end

            else state_next = state_curr;
        end

        else if( state_curr == SHIFT_OPB ) begin

            if( opb_reg[nbits - 2] == 1'b1 ) // MSB will be 1 once shifted
                state_next = CALC;

            else if( opb_reg_sl > opa_reg ) // Don't need to shift any more after this
                state_next = CALC;

            else state_next = state_curr;
        end

        else if( state_curr == CALC ) begin
            if( opb_reg == opb_value )
                state_next = DONE;

            else if( opb_reg == opa_reg ) // Early exit
                state_next = DONE;

            else state_next = state_curr;
        end

        else if( state_curr == DONE ) begin
            if( ostream_rdy )
                state_next = IDLE;

            else state_next = state_curr;
        end

        else state_next = state_curr;
    end

    // Define interface outputs based on FSM state

    assign istream_rdy = ( state_curr == IDLE );
    assign ostream_val = ( state_curr == DONE );

    //--------------------Datapath for Remainder--------------------

    // opa tracks the value that our final result will be
    always @( posedge clk ) begin
        if( reset ) opa_reg <= 0;

        else if( state_curr == IDLE ) begin
            opa_reg <= opa;
        end

        else if( state_curr == CALC ) begin
            if( opb_reg <= opa_reg ) begin // Need to subtract
                opa_reg <= ( opa_reg - opb_reg );
            end
        end
    end

    // opb keeps track of our current divisor
    always @( posedge clk ) begin
        if( reset ) opb_reg <= 0;

        else if( state_curr == IDLE ) begin
            opb_reg <= opb;
        end

        else if( state_curr == SHIFT_OPB ) begin
            opb_reg <= opb_reg_sl; // Shift left until the MSB is 1
        end

        else if( state_curr == CALC ) begin
            opb_reg <= ( opb_reg >> 1 ); // Shift right to divide opa
        end
    end

    // Keep track of our initial divisor with opb_value
    always @( posedge clk ) begin
        if( reset ) opb_value <= 0;

        else if( state_curr == IDLE ) opb_value <= opb;
    end

    //--------------------Datapath for Division--------------------

    // We will keep track of the current quotient in curr_quot,
    // as well as the value that would be added to it at each step
    // in add_quot_val

    logic [nbits - 1:0] curr_quot;
    logic [nbits - 1:0] add_quot_val;

    // add_quot_val logic
    
    always @( posedge clk ) begin

        if( reset ) add_quot_val <= 0;

        else if( state_curr == IDLE ) add_quot_val <= 1;

        // Shift the high bit up as opb shifts up
        else if( state_curr == SHIFT_OPB ) add_quot_val <= add_quot_val << 1;

        // Shift the high bit down as opb shifts down
        else if( state_curr == CALC ) add_quot_val <= add_quot_val >> 1;

    end

    // curr_quot logic

    always @( posedge clk ) begin
        if( reset ) curr_quot <= 0;

        else if( state_curr == IDLE ) curr_quot <= 0;

        else if( state_curr == CALC ) begin

            if( opb_reg <= opa_reg ) // We're subtracting - need to add to remainder

                // Since the high bit in add_quot_val has a corresponding low bit in curr_quot,
                // we can use a bitwise XOR as a quicker way to add
                curr_quot <= curr_quot ^ add_quot_val;
        end
    end

    //--------------------Result Selection--------------------

    // Register the selection

    logic msg_sel_reg;

    always @( posedge clk ) begin

        if( reset ) msg_sel_reg <= 0;

        else if( state_curr == IDLE ) msg_sel_reg <= msg_sel;

    end
    
    // Our remainder output will always be stored in the opa register,
    // and our division output will be in the curr_quot register
    assign ostream_msg = ( msg_sel_reg ) ? opa_reg : curr_quot;

endmodule

`endif // DIV_MOD_DIV_V