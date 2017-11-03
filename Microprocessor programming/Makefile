all: nim.hex

nim.elf: nim.c nokia5110.c
	avr-g++ -mmcu=atmega324a -DF_CPU=16000000 -Wall -Wl,-u,vfprintf -lprintf_flt -lm -O3 -o $@ $^

nim.hex: nim.elf
	avr-objcopy -j .text -j .data -O ihex $^ $@
	avr-size $@

nim.lss: nim.elf
	avr-objdump -t -h -S -C $^ > $@

upload: nim.hex
	sudo ./bootloadHID.2014-03-29/commandline/bootloadHID -r nim.hex

clean:
	rm -rf nim.elf nim.hex nim.lss

.PHONY: all clean