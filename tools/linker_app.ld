OUTPUT_FORMAT(elf32-i386)
OUTPUT_ARCH(i386)
ENTRY(_start)

APP_BASE = 0x02000000;

SECTIONS
{
    . = APP_BASE;

    .text ALIGN(4096) :
    {
        *(.text._start)
        *(.text*)
    }

    .rodata ALIGN(4096) :
    {
        *(.rodata*)
        *(.kef_ui*)
    }

    .data ALIGN(4096) :
    {
        *(.data*)
    }

    .bss ALIGN(4096) :
    {
        __bss_start = .;
        *(.bss*)
        *(COMMON)
        __bss_end = .;
    }

    /DISCARD/ :
    {
        *(.comment*)
        *(.note*)
        *(.eh_frame*)
        *(.gcc_except_table*)
    }
}