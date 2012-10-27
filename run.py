#!/usr/bin/python
import logging
from argparse import ArgumentParser
from pychip16 import Chip16CPU

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

if __name__=='__main__':
    parser = ArgumentParser(description="A Chip-16 emulator implemented in Python")
    parser.add_argument("rom_file", help="Input Chip-16 ROM file")
    parser.add_argument("-l", dest="log_level", default='warning',
            help="The logging level [debug, info, warning, error, critical]")

    args = parser.parse_args()
    cpu = Chip16CPU(args.rom_file, args.log_level)

    cpu.run()
