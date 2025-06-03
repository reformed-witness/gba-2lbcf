#---------------------------------------------------------------------------------
# Simple GBA Makefile for Second London Baptist Confession
#---------------------------------------------------------------------------------

PREFIX := arm-none-eabi-
CC := $(PREFIX)gcc
AS := $(PREFIX)as
OBJCOPY := $(PREFIX)objcopy

TARGET := confession
SOURCES := confession.c crt0.s

CFLAGS := -mthumb -mthumb-interwork -mcpu=arm7tdmi -mtune=arm7tdmi -O2 -Wall
ASFLAGS := -mcpu=arm7tdmi
LDFLAGS := -mthumb -mthumb-interwork -nostartfiles -Tlinker.ld

OBJS := confession.o crt0.o

.PHONY: all clean

all: $(TARGET).gba

$(TARGET).gba: $(TARGET).elf
	@echo "Creating GBA ROM..."
	$(OBJCOPY) -v -O binary $< $@
	@if command -v gbafix >/dev/null 2>&1; then \
		echo "Using gbafix to fix header..."; \
		gbafix $@; \
	else \
		echo "gbafix not found, using Python script..."; \
		python3 fix_header.py $@ || echo "Manual header fix failed - ROM may not load"; \
	fi
	@echo "Built $(TARGET).gba successfully!"

$(TARGET).elf: crt0.o confession.o
	@echo "Linking..."
	$(CC) $(LDFLAGS) crt0.o confession.o -o $@

confession.o: confession.c
	@echo "Compiling confession.c..."
	$(CC) $(CFLAGS) -c $< -o $@

crt0.o: crt0.s
	@echo "Assembling crt0.s..."
	$(AS) $(ASFLAGS) $< -o $@

clean:
	@echo "Cleaning..."
	rm -f *.o *.elf *.gba *.map
	@echo "Clean complete."

# Help target
help:
	@echo "Available targets:"
	@echo "  all     - Build the GBA ROM (default)"
	@echo "  clean   - Remove all built files"
	@echo "  help    - Show this help message"