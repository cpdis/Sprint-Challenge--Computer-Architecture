"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.fl = None
        self.SP = 0xF4
        self.reg[7] = self.ram[self.SP]

        # Instruction table
        self.in_table = {}
        self.in_table[0b00000001] = self.hlt
        self.in_table[0b10000010] = self.ldi
        self.in_table[0b01000111] = self.prn
        self.in_table[0b01000101] = self.push
        self.in_table[0b01000110] = self.pop
        self.in_table[0b01010000] = self.call
        self.in_table[0b00010001] = self.ret
        self.in_table[0b01010100] = self.jmp
        self.in_table[0b01010101] = self.jeq
        self.in_table[0b01010110] = self.jne

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def hlt(self):
        sys.exit()

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def prn(self, operand_a):
        print(self.reg[operand_a])
        self.pc += 2

    def push(self, operand_a):
        # 1. Decrement the `SP`.
        # 2. Copy the value in the given register to the address pointed to by
        # `SP`.
        self.SP -= 1
        value = self.ram[operand_a]
        self.ram[self.SP] = value
        self.pc += 2

    def pop(self, operand_a):
        # 1. Copy the value from the address pointed to by `SP` to the given register.
        # 2. Increment `SP`.
        value = self.ram[self.SP]
        self.reg[operand_a] = value
        self.SP += 1
        self.pc += 2

    def call(self, operand_a):
        # 1. The address of the ** *instruction*** _directly after_ `CALL` is
        # pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
        # 2. The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.
        self.SP -= 1
        next_instruction_address = self.pc + 2
        self.ram[self.SP] = next_instruction_address
        address_to_jump_to = self.ram[operand_a]
        # set PC to the address to jump to
        self.SP = address_to_jump_to

    def ret(self):
        address = self.ram[self.SP]
        self.pc = address
        self.SP += 1

    def jmp(self, operand_a):
        self.pc = self.reg[operand_a]

    def jeq(self, operand_a):
        if self.fl == 0b00000010:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def jne(self, operand_a):
        if self.fl != 0b00000010:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def load(self):
        """Load a program into memory."""

        address = 0

        try:
            # open the program specified by the second command line argument
            with open(sys.argv[1]) as f:
                # for each line in the file
                for line in f:
                    # check if it starts with a binary number
                    if line[0].startswith('0') or line[0].startswith('1'):
                        # only use the first (non-commented) part of the instruction
                        binary = line.split("#")[0]
                        # remove any white space
                        binary = binary.strip()
                        # convert to binary and store it in RAM
                        self.ram[address] = int(binary, 2)
                        address += 1
        except:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found.")

    def alu(self, op, reg_a, reg_b):
        """ALU operations from cheatsheet."""
        ADD = 0b10100000
        MUL = 0b10100010
        SUB = 0b10100001
        DIV = 0b10100011
        # AND = 0b10101000
        OR = 0b10101010
        XOR = 0b10101011
        # NOT = 0b01101001
        SHL = 0b10101100
        SHR = 0b10101101
        # MOD = 0b10100100
        CMP = 0b10100111

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == DIV:
            self.reg[reg_a] /= self.reg[reg_b]
        # elif op == AND:
        #     # TODO
        elif op == OR:
            bit_or = self.reg[reg_a] | self.reg[reg_b]
            self.reg[reg_a] = bit_or
        elif op == XOR:
            xor = self.reg[reg_a] ^ self.reg[reg_b]
            self.reg[reg_a] = xor
        # elif op == NOT:
        #     # TODO
        elif op == SHL:
            shl = self.reg[reg_a]
            left = shl << self.reg[reg_b]
            self.reg[reg_a] = left
        elif op == SHR:
            shr = self.reg[reg_a]
            right = shr >> self.reg[reg_b]
            self.reg[reg_a] = right
        # elif op == MOD:
        #     # TODO
        elif op == CMP:
            a = self.reg[reg_a]
            b = self.reg[reg_b]
            if a == b:
                self.fl = 0b00000010
            elif a < b:
                self.fl = 0b00000100
            elif a > b:
                self.fl = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

        self.pc += 3

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        while True:
            # It needs to read the memory address that's stored in register `PC`, and store
            # that result in `IR`, the _Instruction Register_. This can just be a local
            # variable in `run()`.
            IR = self.ram[self.pc]

            # Using `ram_read()`,read the bytes at `PC+1` and `PC+2` from RAM into variables
            # `operand_a` and `operand_b` in case the instruction needs them.
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Determine number of operands
            cpu_instruct = (IR & 0b11000000) >> 6
            alu_instruct = (IR & 0b00100000) >> 5

            # Handle CALL and RET
            # CALL: calls a subroutine (function) at the address stored in the register.
            if IR == 0b01010000:
                self.in_table[IR](operand_a)
                continue
            # RET: pop the value from the top of the stack and store it in the `PC`.
            elif IR == 0b00010001:
                self.in_table[IR]()
                continue

            # Send the operand to the correct instruction
            if alu_instruct:
                self.alu(IR, operand_a, operand_b)
            elif cpu_instruct == 0:
                self.in_table[IR]()
            elif cpu_instruct == 1:
                self.in_table[IR](operand_a)
            elif cpu_instruct == 2:
                self.in_table[IR](operand_a, operand_b)
            else:
                self.hlt()
