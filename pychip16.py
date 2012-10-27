import logging
import struct
import pygame
import random
from time import sleep, time

LEVELS = {
    'debug':    logging.DEBUG,
    'info':     logging.INFO,
    'warning':  logging.WARNING,
    'error':    logging.ERROR,
    'critical': logging.CRITICAL
}

ARROW_UP = 273
ARROW_DOWN = 274
ARROW_RIGHT = 275
ARROW_LEFT = 276

class Chip16CPU:

  def __init__(self, rom_name, log_level='warning'):
    # load ROM
    self.mem = bytearray(0x10000)
    size = 0
    with open(rom_name, "rb") as rom:
      magick = struct.unpack_from('s', rom.read(4))
      rom.read(2)
      romsize = struct.unpack_from('<L', rom.read(4))[0]
      start = struct.unpack_from('<H', rom.read(2))[0]
      crc = struct.unpack_from('<L', rom.read(4))[0]
      byte = rom.read(1)
      while byte:
        self.mem[size] = ord(byte)
        # FIXME check CRC
        byte = rom.read(1)
        size += 1
      if (size != romsize):
        print "Waiting for ",romsize,"bytes, but ",size," bytes was read"

    self.R = [0x0000]*16
    self.pc = 0x0000
    self.sp = 0xFDF0
    self.stack = []
    self.screen = bytearray(320*240)

    self.log = logging.getLogger("chip16-core")
    self.ch = logging.StreamHandler()
    self.ch.setLevel(logging.DEBUG)
    self.log.addHandler(self.ch)
    self.log.setLevel(LEVELS[log_level])
    self.loglevel = LEVELS[log_level]
    self.logEnabled = True

  def writeMem(self, addr, data):
    packed = struct.pack('<H', data)
    for i,byte in enumerate(packed):
      self.mem[addr+i] = byte

  def readMem(self, addr):
    unpacked = struct.unpack('<L', str(self.mem[addr:addr+4]))[0]
    return unpacked

  def pushStack(self, value):
    if len(self.stack) >= 512:
      raise Exception('Stack Overflow!')
    self.stack.append(value)

  def popStack(self):
    if len(self.stack) == 0:
      raise Exception('Stack Underflow!')
    return self.stack.pop()

  def updateScreen(self):
    # FIXME stub
    return

  def getInput(self):
    # FIXME stub
    return

  def runOpcode(self, opcode):
    # FIXME stub
    self.log.info('[0x%04X]: 0x%08X' % (self.pc, opcode))
    x = (opcode & 0x0F0000) >> 16
    y = (opcode & 0xF00000) >> 20
    n = (opcode & 0x0F00) >> 8
    ll = (opcode & 0xFF00) >> 8
    hh = opcode & 0xFF
    self.log.debug('x:0x%02X y:0x%02X n:0x%02X ll:0x%02X hh:0x%02X' % (x,y,n,ll,hh))
    for i,val in enumerate(self.R):
      self.log.debug('R%x: 0x%04X' % (i, val))
    self.pc += 1
    return

  def run(self):
    ftime = time()
    while self.pc <=0xFFFF-4:
      self.updateScreen()
      #pygame.display.update()

      # VBLANK
      if (time()-ftime) > 1.0/60:
        ftime = time()
        self.updateScreen()
        #pygame.display.update()

      opcode = self.readMem(self.pc)
      try:
        self.runOpcode(opcode)
      except Exception as e:
        print e
        return False

    print "I'm done."
