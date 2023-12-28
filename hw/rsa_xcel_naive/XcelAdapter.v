//=========================================================================
// XcelAdapter.v
//=========================================================================
// Adapter for allowing the modular exponentiation to interface with the
// xcel protocol
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

`ifndef RSA_XCEL_NAIVE_XCELADAPTER_V
`define RSA_XCEL_NAIVE_XCELADAPTER_V

`include "vc/mem-msgs.v"
`include "vc/xcel-msgs.v"
`include "vc/queues.v"

module rsa_xcel_naive_XcelAdapter
(
    input  logic         clk,
    input  logic         reset,

    // Xcel Input Interface

    input  xcel_req_t    xcel_reqstream_msg,
    input  logic         xcel_reqstream_val,
    output logic         xcel_reqstream_rdy,

    // Xcel Output Interface

    output xcel_resp_t   xcel_respstream_msg,
    output logic         xcel_respstream_val,
    input  logic         xcel_respstream_rdy,

    // ModExp istream Interface

    output logic [95:0]  modexp_istream_msg,
    output logic         modexp_istream_val,
    input  logic         modexp_istream_rdy,

    // ModExp ostream Interface

    input  logic [31:0]  modexp_ostream_msg,
    input  logic         modexp_ostream_val,
    output logic         modexp_ostream_rdy
);

    // 4-state sim fix: force outputs to be zero if invalid

    xcel_resp_t xcel_respstream_msg_raw;
    assign xcel_respstream_msg = xcel_respstream_msg_raw & {33{xcel_respstream_val}};

    // Accelerator ports and queues

    logic      xcelreq_deq_val;
    logic      xcelreq_deq_rdy;
    xcel_req_t xcelreq_deq_msg;

    vc_Queue#(`VC_QUEUE_PIPE,$bits(xcel_req_t),1) xcelreq_q
    (
      .clk     (clk),
      .reset   (reset),
      .num_free_entries(),

      .enq_val (xcel_reqstream_val),
      .enq_rdy (xcel_reqstream_rdy),
      .enq_msg (xcel_reqstream_msg),

      .deq_val (xcelreq_deq_val),
      .deq_rdy (xcelreq_deq_rdy),
      .deq_msg (xcelreq_deq_msg)
    );

    //---------------------------------------------------------
    // Control
    //---------------------------------------------------------

    // Define states

    localparam IDLE = 2'd0;
    localparam SEND = 2'd1;
    localparam RECV = 2'd2;
    localparam DONE = 2'd3;

    // Define state transitions

    logic is_write;
    assign is_write = ( xcelreq_deq_msg.type_ == `VC_XCEL_REQ_MSG_TYPE_WRITE );

    logic [1:0] state_curr;
    logic [1:0] state_next;

    always @( posedge clk ) state_curr <= state_next;

    always @( * ) begin

        // Default
        state_next = state_curr;

        if( reset ) state_next = IDLE;

        else if( state_curr == IDLE ) begin

            if( xcelreq_deq_val & xcelreq_deq_rdy & is_write & ( xcelreq_deq_msg.addr == 0 ) ) begin
                // We can go to sending the message on
                state_next = SEND;
            end
        end

        else if( state_curr == SEND ) begin

            if( modexp_istream_rdy ) begin
                // Transaction happened
                state_next = RECV;
            end
        end

        else if( state_curr == RECV ) begin

            if( modexp_ostream_val ) begin
                // Can receive
                state_next = DONE;
            end
        end

        else if( state_curr == DONE ) begin

            if( xcel_respstream_rdy ) begin
                // Processor can receive response
                state_next = IDLE;
            end
        end
    end

    //---------------------------------------------------------
    // Data
    //---------------------------------------------------------

    // Input data registers

    logic [31:0] base_reg;
    logic [31:0] exp_reg;
    logic [31:0] mod_reg;

    always @( posedge clk ) begin

        if( reset ) begin
            base_reg <= 32'b0;
            exp_reg  <= 32'b0;
            mod_reg  <= 32'b0;
        end

        else if( ( state_curr == IDLE ) & xcelreq_deq_val & xcelreq_deq_rdy & is_write ) begin

            if( xcelreq_deq_msg.addr == 1 ) // Base register
                base_reg <= xcelreq_deq_msg.data;

            else if( xcelreq_deq_msg.addr == 2 ) // Exponent register
                exp_reg <= xcelreq_deq_msg.data;

            else if( xcelreq_deq_msg.addr == 3 ) // Modulus register
                mod_reg <= xcelreq_deq_msg.data;
        end
    end

    // Output data register

    logic [31:0] result;

    always @( posedge clk ) begin

        if( reset ) result <= 32'b0;

        else if( ( state_curr == RECV ) & modexp_ostream_val ) // Register the result
            result <= modexp_ostream_msg;
    end

    // Form modexp outputs

    assign modexp_istream_msg[31:0]  = base_reg;
    assign modexp_istream_msg[63:32] = exp_reg;
    assign modexp_istream_msg[95:64] = mod_reg;

    assign modexp_istream_val = ( state_curr == SEND );

    assign modexp_ostream_rdy = ( state_curr == RECV );

    // Form xcel outputs

    always @( * ) begin

        if( state_curr == IDLE ) begin
            // Send write response back, if any
            xcelreq_deq_rdy     = xcel_respstream_rdy;
            xcel_respstream_val = xcelreq_deq_val;

            xcel_respstream_msg_raw.data  = 32'b0;
            xcel_respstream_msg_raw.type_ = `VC_XCEL_RESP_MSG_TYPE_WRITE;
        end

        else if( state_curr == DONE ) begin
            // We will be sending the result back
            xcelreq_deq_rdy     = xcel_respstream_rdy;
            xcel_respstream_val = xcelreq_deq_val;

            xcel_respstream_msg_raw.data   = result;
            xcel_respstream_msg_raw.type_  = `VC_XCEL_RESP_MSG_TYPE_READ;
        end

        else begin
            xcelreq_deq_rdy     = 0;
            xcel_respstream_val = 0;

            xcel_respstream_msg_raw.data   = 32'b0;
            xcel_respstream_msg_raw.type_  = `VC_XCEL_RESP_MSG_TYPE_X;
        end
    end

endmodule

`endif // RSA_XCEL_NAIVE_XCELADAPTER_V