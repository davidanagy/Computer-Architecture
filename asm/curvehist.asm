; Prints the following curve:
; (each line has twice as many asterisks as the previous)
; *
; **
; ****
; ********
; ****************
; ********************************
; ****************************************************************
; MAIN:

    LDI R0,1                ; Number of asterisks
    LDI R1,1                ; Line we're about to print to
    LDI R2,7                ; Final line we want to print to
    LDI R3,PrintCurve       ; Address of PrintCurve
    LDI R4,AsterisksLoop    ; Address of AsterisksLoop
    CALL R3                 ; Call PrintCurve
    HLT                     ; Halt

; Subroutine: PrintCurve
; Print the number of asterisks in R0
; Increment R1 by 1
; If R1 > R2, stop

PrintCurve:

    PUSH R1
    LDI R1,0                    ; Number of asterisks printed on this line
    PUSH R2
    LDI R2,42                   ; Asterisk
    PUSH R3
    LDI R3,AsterisksLoopEnd     ; Address of AsterisksLoopEnd
    CALL R4                     ; Call AsterisksLoop
    POP R3
    POP R2
    POP R1
    INC R1          ; Increment R1
    CMP R1,R2       ; Compare R1 and R2
    PUSH R0
    LDI R0,LoopEnd  ; Address of LoopEnd
    JGT R0          ; Jump to LoopEnd if R1 > R2
    POP R0
    PUSH R1
    LDI R1,2
    MUL R0,R1
    LDI R1,10       ; Newline character
    PRA R1
    POP R1
    JMP R3          ; Re-run PrintCurve

AsterisksLoop:

    PRA R2          ; Print asterisk
    INC R1
    CMP R1,R0
    JEQ R3
    JMP R4

AsterisksLoopEnd:

    RET

LoopEnd:

    RET