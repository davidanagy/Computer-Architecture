# Write a program in Python that runs programs

PRINT_BEEJ = 1
HALT = 2
SAVE_REG = 3 # Store a value in a register (in the LS8 called LDI)
PRINT_REG = 4 # corresponds to PRN in the LS8

memory = [
    PRINT_BEEJ,
    SAVE_REG,       # SAVE R0,37    store 37 in R0      the opcode--the instruction itself
    0,              # R0        operand--argument
    37,             # 37        operand--argument
    PRINT_BEEJ,
    PRINT_REG,      # PRINT_REG R0
    0,              # R0
    HALT
]

register = [0] * 8 # like variables R0-R7. Hold values/numbers

pc = 0 # Program Counter: The address (in memory) of the current instruction
running = True

while running:
    inst = memory[pc]

    if inst == PRINT_BEEJ:
        print('Beej!')
        pc += 1

    elif inst == SAVE_REG:
        op0 = memory[pc+1]
        op1 = memory[pc+2]
        register[op0] = op1
        pc += 3

    elif inst == PRINT_REG:
        op = memory[pc+1]
        print(register[op])
        pc += 2

    elif inst == HALT:
        running = False

    else:
        print('Unknown instruction')
        running = False
