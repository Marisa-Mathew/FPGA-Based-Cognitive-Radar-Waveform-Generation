
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 28.06.2026 20:07:54
// Design Name: 
// Module Name: nlfm_waveform_gen
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

`timescale 1ns / 1ps

module nlfm_waveform_gen
#(
    parameter ADDR_WIDTH = 10,
    parameter DEPTH      = 625
)
(
    input  wire clk,
    input  wire rst,
    input  wire start,

    output reg signed [15:0] out_i,
    output reg signed [15:0] out_q,
    output reg valid,
    output reg done
);

    //--------------------------------------------------
    // ROM Interface
    //--------------------------------------------------

    reg  [ADDR_WIDTH-1:0] rom_addr;
    wire [31:0] rom_data;

    blk_mem_gen_0 rom_inst
    (
        .clka(clk),
        .ena(1'b1),
        .addra(rom_addr),
        .douta(rom_data)
    );

    //--------------------------------------------------
    // State Machine
    //--------------------------------------------------

    localparam IDLE = 2'd0;
    localparam RUN  = 2'd1;
    localparam LAST = 2'd2;

    reg [1:0] state;

    //--------------------------------------------------
    // Sample Counter
    //--------------------------------------------------

    reg [ADDR_WIDTH-1:0] sample_count;

    //--------------------------------------------------
    // Main Logic
    //--------------------------------------------------

    always @(posedge clk)
    begin

        if(rst)
        begin

            state        <= IDLE;
            rom_addr     <= 0;
            sample_count <= 0;

            out_i <= 0;
            out_q <= 0;

            valid <= 0;
            done  <= 0;

        end

        else
        begin

            case(state)

            //--------------------------------------------------
            // IDLE
            //--------------------------------------------------

            IDLE:
            begin

                valid <= 0;
                done  <= 0;

                rom_addr     <= 0;
                sample_count <= 0;

                if(start)
                begin
                    state <= RUN;
                end

            end

            //--------------------------------------------------
            // RUN
            //--------------------------------------------------

            RUN:
            begin

                valid <= 1;

                // Output previous ROM data
                out_i <= rom_data[31:16];
                out_q <= rom_data[15:0];

                if(sample_count < DEPTH-1)
                begin
                    sample_count <= sample_count + 1;
                    rom_addr <= rom_addr + 1;
                end
                else
                begin
                    state <= LAST;
                end

            end

            //--------------------------------------------------
            // LAST SAMPLE
            //--------------------------------------------------

            LAST:
            begin

                // Capture the final ROM output
                out_i <= rom_data[31:16];
                out_q <= rom_data[15:0];

                valid <= 1;
                done  <= 1;

                state <= IDLE;

            end

            endcase

        end

    end

endmodule
