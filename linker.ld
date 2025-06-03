OUTPUT_FORMAT("elf32-littlearm", "elf32-bigarm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(_start)

MEMORY {
    rom (rx) : ORIGIN = 0x08000000, LENGTH = 32M
    iwram (rwx) : ORIGIN = 0x03000000, LENGTH = 32K
    ewram (rwx) : ORIGIN = 0x02000000, LENGTH = 256K
}

SECTIONS {
    . = 0x08000000;
    
    .text : {
        KEEP(*(.text))
        *(.text.*)
        *(.glue_7)
        *(.glue_7t)
        *(.rodata .rodata.*)
        . = ALIGN(4);
    } > rom
    
    .data : {
        __data_start = .;
        *(.data .data.*)
        . = ALIGN(4);
        __data_end = .;
    } > iwram AT > rom
    
    __data_load = LOADADDR(.data);
    
    .bss : {
        __bss_start = .;
        *(.bss .bss.*)
        *(COMMON)
        . = ALIGN(4);
        __bss_end = .;
    } > iwram
    
    . = ALIGN(4);
    __end = .;
    
    /* Stack addresses */
    __sp_irq = 0x03007FA0;
    __sp_usr = 0x03008000;
    
    /* Remove debug sections */
    /DISCARD/ : {
        *(.comment)
        *(.debug*)
        *(.ARM.attributes)
    }
}