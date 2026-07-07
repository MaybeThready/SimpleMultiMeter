/*
 * 组件模块，包含FPGA常用组件
 */

/** N进制计数器
* clk: 时钟信号
* rstn: 复位信号，低电平有效
* count: 当前计数值，范围为0~N-1
* carry: 进位信号，当计数器从N-1回到0时，carry为1
* param N: 计数器的进制，默认为32
* param INITIAL_CNT: 计数器的初始值，默认为0
*/
module CTU
#(
    parameter N = 32,
    parameter INITIAL_CNT = 0
)
(
    input clk, rstn,
    output [$clog2(N)-1:0] count,
    output carry
);
    reg [$clog2(N)-1:0] r_count;
    reg r_carry;
    always @(posedge clk or negedge rstn)
    begin
        if (!rstn)
        begin
            r_count <= INITIAL_CNT;
            r_carry <= 1'b0;
        end
        else if (count == N - 1)
        begin
            r_count <= 0;
            r_carry <= 1'b1;
        end
        else
        begin
            r_count <= r_count + 1'b1;
            r_carry <= 1'b0;
        end
    end

    assign count = r_count;
    assign carry = r_carry;
endmodule

/** 分频器
* clk: 输入时钟信号
* rstn: 复位信号，低电平有效
* clk_div: 输出的分频时钟信号
* param NUM_DIV: 分频系数，必须为偶数，默认为10
*/
module DIV
#(
    parameter NUM_DIV = 10
)
(
    input clk, rstn,
    output clk_div
);
    localparam MAX_CNT = (NUM_DIV >> 1) - 1;

    reg r_clk_div;
    reg [$clog2(NUM_DIV>>1'b1)-1 : 0] count;
 
    always @(posedge clk or negedge rstn)
    begin
        if (!rstn)
        begin
            count <= 0;
            r_clk_div <= 1'b0;
        end
        else if (count < MAX_CNT)
        begin
            count <= count + 1'b1;
        end
        else
        begin
            count <= 0;
            r_clk_div <= ~r_clk_div;
        end
    end

    assign clk_div = r_clk_div;
endmodule



/** 二进制数转BCD码
* param W: 二进制位宽
* bin: W位二进制输入
* bcd: BCD码输出，每4位表示一个十进制数
*/
module BIN2BCD
#(
    parameter W = 16,
    parameter BCD_WIDTH = W + (W - 4) / 3 + 1
)
(
    input  [W-1:0] bin,
    output [BCD_WIDTH-1:0] bcd
);

    localparam NUM_DIGITS = BCD_WIDTH / 4;

    reg [BCD_WIDTH-1:0] bcd_temp;
    integer i, j;

    always @(*)
    begin
        // 清零
        bcd_temp = {BCD_WIDTH{1'b0}};

        // Double Dabble
        for (i = W-1; i >= 0; i = i - 1)
        begin
            // Step1：所有BCD位>=5则加3
            for (j = 0; j < NUM_DIGITS; j = j + 1)
            begin
                if (bcd_temp[j*4 +: 4] >= 5)
                    bcd_temp[j*4 +: 4] = bcd_temp[j*4 +: 4] + 4'd3;
            end

            // Step2：整体左移一位，移入新的二进制位
            bcd_temp = {bcd_temp[BCD_WIDTH-2:0], bin[i]};
        end
    end

    assign bcd = bcd_temp;

endmodule

// module UnsignedFixedPoint2BCD
// #(
//     parameter Q_IN_INT = 16,
//     parameter Q_IN_FRAC = 16,
//     parameter BCD_INT_NUM = 3,
//     parameter BCD_FRAC_NUM = 3
// )
// (
//     input clk, rstn,
//     input [Q_IN_INT + Q_IN_FRAC - 1:0] in,
//     output [BCD_INT_NUM*4 + BCD_FRAC_NUM*4 - 1:0] bcd
// );
//     wire [BCD_INT_NUM*4 - 1:0] bcd_int;
//     wire [BCD_FRAC_NUM*4 - 1:0] bcd_frac;
    
//     wire [Q_IN_INT-1:0] int_part = in[Q_IN_INT + Q_IN_FRAC - 1:Q_IN_FRAC];
//     wire [Q_IN_FRAC-1:0] frac_part = in[Q_IN_FRAC-1:0];

//     localparam DESIRE_INT_WIDTH = $clog2(10**BCD_INT_NUM);
//     wire [DESIRE_INT_WIDTH-1:0] norm_int;
//     UnsignedFixedPointNorm #(
//         .Q_IN_INT(Q_IN_INT),
//         .Q_IN_FRAC(0),
//         .Q_OUT_INT(DESIRE_INT_WIDTH),
//         .Q_OUT_FRAC(0)
//     ) norm_int_inst
//     (
//         .in(int_part),
//         .out(norm_int)
//     );

//     BIN2BCD #(
//         .W(DESIRE_INT_WIDTH),
//         .BCD_WIDTH(BCD_INT_NUM*4)
//     ) int_bin2bcd_inst
//     (
//         .bin(norm_int),
//         .bcd(bcd_int)
//     );

//     localparam DESIRE_FRAC_WIDTH = $clog2(10**BCD_FRAC_NUM);
//     wire [DESIRE_FRAC_WIDTH-1:0] norm_frac;

//     UnsignedFixedPointMult #(
//         .Q_IN_INT_A(0),
//         .Q_IN_FRAC_A(Q_IN_FRAC),
//         .Q_IN_INT_B(DESIRE_FRAC_WIDTH),
//         .Q_IN_FRAC_B(0),
//         .Q_OUT_INT(DESIRE_FRAC_WIDTH),
//         .Q_OUT_FRAC(0)
//     ) mult_inst
//     (
//         .clk(clk),
//         .rstn(rstn),
//         .in_a(frac_part),
//         .in_b(10**BCD_FRAC_NUM),
//         .out(norm_frac)
//     );

//     BIN2BCD #(
//         .W(DESIRE_FRAC_WIDTH),
//         .BCD_WIDTH(BCD_FRAC_NUM*4)
//     ) frac_bin2bcd_inst
//     (
//         .bin(norm_frac),
//         .bcd(bcd_frac)
//     );

//     reg [BCD_INT_NUM*4 + BCD_FRAC_NUM*4 - 1:0] r_bcd;
//     reg [BCD_INT_NUM*4 - 1:0] bcd_int_prev;  // 整数计算要快一点，所以要延后
//     always @(posedge clk or negedge rstn)
//     begin
//         if (!rstn)
//         begin
//             bcd_int_prev <= 0;
//             r_bcd <= 0;
//         end
//         else
//         begin
//             bcd_int_prev <= bcd_int;
//             r_bcd <= {bcd_int_prev, bcd_frac};
//         end
//     end

//     assign bcd = r_bcd;
// endmodule

/** 有限状态机
* clk: 时钟信号
* rstn: 复位信号，低电平有效
* stn: 下一个状态输入
* initial_state: 初始状态，复位时stc被设置为该值
* stc: 当前状态
*/
module FSM
#(
    parameter N = 4,
    parameter INITIAL_STATE = 0
)
(
    input clk, rstn,
    input [$clog2(N)-1:0] stn,
    output [$clog2(N)-1:0] stc
);
    reg [$clog2(N)-1 : 0] r_stc;

    always @(posedge clk or negedge rstn)
    begin
        if (!rstn)
        begin
            r_stc <= INITIAL_STATE;
        end
        else
        begin
            r_stc <= stn;
        end
    end

    assign stc = r_stc;
endmodule
