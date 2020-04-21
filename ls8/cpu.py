"""CPU functionality."""

from datetime import datetime
import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xf4
        self.pc = 0
        # self.inst_branchtable = {
        #     'CALL': self.call,
        #     'LD': self.ld,
        #     'LDI': self.ldi,
        #     'JMP': self.jmp,
        #     'NOP': self.nop,
        #     'POP': self.pop,
        #     'PRA': self.pra,
        #     'PRN': self.prn,
        #     'PUSH': self.push,
        #     'RET': self.ret,
        #     'ST': self.st
        # }
        self.dictionary = {
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
        self.fl = 0b00000000

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
        elif op == 'AND':
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = self.fl | 0b00000001
                self.fl = self.fl & 0b11111001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = self.fl | 0b00000100
                self.fl = self.fl & 0b11111100
            else:
                self.fl = self.fl | 0b00000010
                self.fl = self.fl & 0b11111010
        elif op == 'DEC':
            self.reg[reg_a] -= 1
        elif op == 'DIV':
            self.reg[reg_a] = self.reg[reg_a] / self.reg[reg_b]
        elif op == 'INC':
            self.reg[reg_a] += 1
        elif op == 'MOD':
            self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'NOT':
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == 'OR':
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == 'SHL':
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == 'SHR':
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'XOR':
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")
        self.reg[reg_a] = self.reg[reg_a] & 0xff

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

    def _decode(self, byte):
        """Decodes byte into the proper instruction string"""
        return self.dictionary[byte]

    def _judge(self, mask, shift=False, shift_amount=None):
        self.push(5)
        self.push(6)
        self.ldi(5, self.fl)
        self.ldi(6, mask)
        self.alu('AND', 5, 6)
        if shift:
            self.ldi(6, shift_amount)
            self.alu('SHR', 5, 6)
        if self.reg[5] == 0:
            self.pop(6)
            self.pop(5)
            return False
        else:
            self.pop(6)
            self.pop(5)
            return True

    def _check_elapsed_time(self):
        for i in range(3):
            self.push(i)
        self.ldi(0, 0xf7)
        self.ldi(1, datetime.now())
        self.ld(2, 0)
        self.alu('INC', 2, None)
        self.alu('CMP', 1, 2)
        if self._judge(mask=0b00000011):
            self.push(3)
            self.ldi(3, 0b00000001)
            self.alu('OR', 6, 3)
            self.pop(3)
            self.st(1, 0)
        for i in reversed(range(3)):
            self.pop(i)

    def call(self, register):
        # Save current value of reg[4] to reserved place in RAM
        self.ram_write(self.reg[4], 0xf5)
        # Change reg[4] to address of next instruction
        self.ldi(4, self.pc+2)
        # Push addres of next instruction to stack
        self.push(4)
        # Return reg[4] to its original value
        self.ldi(4, self.ram_read(0xf5))
        # Set PC to address in given register
        self.pc = self.reg[register]

    def jeq(self, register):
        if self._judge(mask=0b00000001):
            self.jmp(register)

    def jge(self, register):
        if self._judge(mask=0b00000011):
            self.jmp(register)

    def jgt(self, register):
        if self._judge(mask=0b00000010, shift=True, shift_amount=1):
            self.jmp(register)

    def jle(self, register):
        if self._judge(mask=0b00000101):
            self.jmp(register)

    def jlt(self, register):
        if self._judge(mask=0b00000100, shift=True, shift_amount=2):
            self.jmp(register)

    def jmp(self, register):
        self.pc = self.reg[register]

    def jne(self, register):
        if not self._judge(mask=0b00000001):
            self.jmp(register)

    def ld(self, reg_a, reg_b):
        mar = self.reg[reg_b]
        mdr = self.ram_read(mar)
        self.reg[reg_a] = mdr

    def ldi(self, register, imm):
        self.reg[register] = imm

    def nop(self):
        pass

    def pop(self, register):
        sp = self.reg[7]
        self.reg[register] = self.ram[sp]
        self.reg[7] += 1

    def pra(self, register):
        print(chr(self.reg[register]))

    def prn(self, register):
        print(self.reg[register])

    def push(self, register):
        self.reg[7] -= 1
        sp = self.reg[7]
        self.ram[sp] = self.reg[register]

    def ret(self):
        # Save current value of reg[4] to reserved place in RAM
        self.ram_write(self.reg[4], 0xf5)
        # Pop value from top of stack
        self.pop(4)
        # Set that value as the PC
        self.pc = self.reg[4]
        # Return reg[4] to its previous state
        self.reg[4] = self.ram_read(0xf5)

    def st(self, reg_a, reg_b):
        mdr = self.reg[reg_a]
        mar = self.reg[reg_b]
        self.ram_write(mdr, mar)

    def run(self):
        """Run the CPU."""
        self.ldi(0, datetime.now())
        self.ldi(1, 0xf7)
        self.st(0, 1)
        while True:
            self._check_elapsed_time()
            if self.reg[6] == 1:
                maskedInterrupts = self.reg[5] & self.reg[6]
                for i in range(8):
                    # Right shift interrupts by i, then mask with 1
                    if ((maskedInterrupts >> i) & 1) == 1:
                        # 1. Disable further interrupts (this will be done later)
                        # 2. Clear the bit in the IS register
                        is_bit_mask = ''
                        for _ in range(i):
                            is_bit_mask += '1'
                        is_bit_mask += '0'
                        while len(is_bit_mask) < 8:
                            is_bit_mask += '1'
                        # Save reg[0] to reserved place in memory
                        self.ram_write(self.reg[0], 0xf5)
                        self.ldi(0, int(is_bit_mask, 2))
                        self.alu('AND', 6, 0)
                        # 3. Push PC register onto the stack
                        self.ldi(0, self.pc)
                        self.push(0)
                        # 4. Push FL register onto the stack
                        self.ldi(0, self.fl)
                        self.push(0)
                        # 5. Push registers R0-R6 onto the stack in that order.
                        # Bring back original value of reg[0]
                        self.reg[0] = self.ram_read(0xf5)
                        for j in range(7):
                            self.push(j)
                        # 6. Look up vector of the appropriate handler
                        vector_address = 0xf8+i
                        # 7. Set the PC to the vector address
                        self.pc = vector_address
                        # (Disable further interrupts)
                        self.ldi(5, 0)
            ir = self.ram_read(self.pc)
            inst = self._decode(ir)
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            # This helped to learn how to isolate values in a bit:
            # https://stackoverflow.com/a/45221136/12685847
            # Isolate first two values to get the number of operands
            num_ops = ir >> 6 & 0b11
            is_alu = ir >> 5 & 1 # Isolate the 3rd value
            inst_sets_pc = ir >> 4 & 1 # Isolate the 4th value
            next_inst_loc = self.pc + num_ops+1
            if inst == 'HLT':
                self.pc = next_inst_loc
                break
            elif is_alu:
                self.alu(inst, operand_a, operand_b)
                self.pc = next_inst_loc
            else:
                func = getattr(self, inst.lower())
                if num_ops == 0:
                    func()
                elif num_ops == 1:
                    func(operand_a)
                else:
                    func(operand_a, operand_b)

            if not inst_sets_pc:
                self.pc = next_inst_loc