"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xf4
        self.pc = 0
        self.inst_branchtable = {
            'LDI': self.ldi,
            'POP': self.pop,
            'PRN': self.prn,
            'PUSH': self.push
        }

    def ram_read(self, mar):
        """Returns value stored in the given RAM address"""
        mdr = self.ram[mar]
        return mdr

    def ram_write(self, mdr, mar):
        """Writes a value into RAM at the given address"""
        self.ram[mar] = mdr

    def load(self, filename):
        """Opens file, reads it line by line, and loads them into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        with open(filename) as f:
            program = f.readlines()
        for line in program:
            if '#' in line:
                instruction = line.split('#')[0]
            else:
                instruction = line.split('\n')[0]
            if len(instruction) == 0:
                continue
            else:
                #print(f'writing {instruction}')
                instruction = int(instruction, 2)
                self.ram_write(instruction, address)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def decode(self, bite):
        """Decodes bite into the proper instruction string"""
        dictionary = {
            0b10100000: 'ADD',
            0b10101000: 'AND',
            0b01010000: 'CALL',
            0b10100111: 'CMP',
            0b01100110: 'DEC',
            0b10100011: 'DIV',
            0b00000001: 'HLT',
            0b01100101: 'INC',
            0b01010010: 'INT',
            0b00010011: 'IRET',
            0b01010101: 'JEQ',
            0b01011010: 'JGE',
            0b01010111: 'JGT',
            0b01011001: 'JLE',
            0b01011000: 'JLT',
            0b01010100: 'JMP',
            0b01010110: 'JNE',
            0b10000011: 'LD',
            0b10000010: 'LDI',
            0b10100100: 'MOD',
            0b10100010: 'MUL',
            0b00000000: 'NOP',
            0b01101001: 'NOT',
            0b10101010: 'OR',
            0b01000110: 'POP',
            0b01001000: 'PRA',
            0b01000111: 'PRN',
            0b01000101: 'PUSH',
            0b00010001: 'RET',
            0b10101100: 'SHL',
            0b10101101: 'SHR',
            0b10000101: 'ST',
            0b10100001: 'SUB',
            0b10101011: 'XOR'
        }

        return dictionary[bite]

    def ldi(self, reg_loc, value):
        self.reg[reg_loc] = value

    def pop(self, reg_loc):
        sp = self.reg[7]
        self.reg[reg_loc] = self.ram[sp]
        self.reg[7] += 1

    def prn(self, reg_loc):
        print(self.reg[reg_loc])

    def push(self, reg_loc):
        self.reg[7] -= 1
        sp = self.reg[7]
        self.ram[sp] = self.reg[reg_loc]

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            ir = self.ram_read(self.pc)
            inst = self.decode(ir)

            # This helped to learn how to isolate values in a bit:
            # https://stackoverflow.com/a/45221136/12685847
            num_ops = ir >> 6 & 0b11 # Isolate the first two values
            if num_ops > 0:
                operand_a = self.ram_read(self.pc+1)
            if num_ops == 2:
                operand_b = self.ram_read(self.pc+2)

            is_alu = ir >> 5 & 1 # Isolate the 3rd value
            if inst == 'HLT':
                running = False
            elif is_alu:
                self.alu(inst, operand_a, operand_b)
            else:
                func = self.inst_branchtable[inst]
                if num_ops == 0:
                    func()
                elif num_ops == 1:
                    func(operand_a)
                else:
                    func(operand_a, operand_b)

            self.pc += num_ops+1
