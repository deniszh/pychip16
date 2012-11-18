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
    self.pc = start
    self.sp = 0xFDF0
    self.stack = []
    self.screen = bytearray(320*240)
    self.flag_c = self.flag_z = self.flag_o = self_flag.n = 0
    self.flip_x = self.flip_y = 0
    self.vblnk = false

    self.log = logging.getLogger("chip16-core")
    self.ch = logging.StreamHandler()
    self.ch.setLevel(logging.DEBUG)
    self.log.addHandler(self.ch)
    self.log.setLevel(LEVELS[log_level])
    self.loglevel = LEVELS[log_level]
    self.logEnabled = True

    self.palette = [(0x00,0x00,0x00),
                    (0x00,0x00,0x00),
                    (0x88,0x88,0x88),
                    (0xBF,0x39,0x32),
                    (0xDE,0x7A,0xAE),
                    (0x4C,0x3D,0x21),
                    (0x90,0x5F,0x25),
                    (0xE4,0x94,0x52),
                    (0xEA,0xD9,0x79),
                    (0x53,0x7A,0x3B),
                    (0xAB,0xD5,0x4A),
                    (0x25,0x2E,0x38),
                    (0x00,0x46,0x7F),
                    (0x68,0xAB,0xCC),
                    (0xBC,0xDE,0xE4),
                    (0xFF,0xFF,0xFF)]
    pygame.init()
    self.bgc = 0x01
    self.sprW = self.sprH = 0
    self.window = pygame.display.set_mode((320,240))
    self.window.fill(self.palette[self.bgc])

  def cond(self, cond):
    if cond == 0x0:
      return self.flag_z
    elif cond == 0x01:
      return not self.flag_z
    elif cond == 0x02:
      return self.flag_n
    elif cond == 0x03:
      return not self.flag_n
    elif cond == 0x04:
      return self.flag_n && self.flag_z
    elif cond == 0x05:
      return self.flag_o
    elif cond == 0x06:
      return not self.flag_o
    elif cond == 0x07:
      return self.flag_c && self.flag_z
    elif cond == 0x08:
      return not self.flag_c
    elif cond == 0x09:
      return self.flag_c
    elif cond == 0x0a:
      return self.flag_c || self.flag_z
    elif cond == 0x0b:
      return self.flag_o == self.flag_n && not self.flag_z
    elif cond == 0x0c:
      return self.flag_o == self.flag_n
    elif cond == 0x0d:
      return self.flag_o != self.flag_n
    elif cond == 0x0e:
      return self.flag_o != self.flag_n || sef.flag_z
    else:
      self.log.warning('WROND CONDITION')
      return false

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
    ll = (opcode & 0xFF00) >> 8
    hh = opcode & 0xFF
    hhll = opcode & 0xFFFF
    a = (opcode & 0xFF000000) >> 24
    n = (opcode & 0x0F00) >> 8
    self.log.debug('a:0x%02X x:0x%02X y:0x%02X n:0x%02X ll:0x%02X hh:0x%02X' % (a,x,y,n,ll,hh))
    for i,val in enumerate(self.R):
      self.log.debug('R%x: 0x%04X' % (i, val))

    # main decode cycle
    self.pc =+ 1
    # NOOP
    if opcode == 0x0:
       pass
    # CLS
    elif a == 0x01:
      self.window.fill(self.palette[self.bgc])
    # VBLNK
    elif a == 0x02:
      self.vblnk = true
      self.log.warning('TODO VBLNK')
    # BGC N
    elif a == 0x03:
      self.bgc = n
      #self.window.fill(self.palette[self.bgc])
    # SPR HHLL
    elif a == 0x04:
      self.sprH = hh
      self.sprW = ll
    # DRW RX, RY, HHLL
    elif a == 0x05:
      self.log.warning('TODO DRW RX, RY, HHLL')
    # DRW RX, RY, RZ
    elif a == 0x06:
      self.log.warning('TODO DRW RX, RY, RZ')
    # RND RX, HHLL
    elif a == 0x07:
      self.R[x] = random.randrange(hhll)
    # FLIP X, Y
    elif a == 0x08:
      self.flip_x = hhll >> 9
      delf.flip_y = hhll >> 8 && 0x01
    # SND0
    elif a == 0x09:
      self.log.warning('TODO SND0')
    # SND1 HHLL
    elif a == 0x0a:
      self.log.warning('TODO SND1 HHLL')
    # SSND2 HHLL
    elif a == 0x0b:
      self.log.warning('TODO SSND2 HHLL')
    # SND3 HHLL
    elif a == 0x0c:
      self.log.warning('TODO SND3 HHLL')
    # SNP RX, HHLL
    elif a == 0x0d:
      self.log.warning('TODO SNP RX, HHLL')
    # SNG AD, VTSR
    elif a == 0x0e:
      self.log.warning('TODO SNG AD, VTSR')
    # JMP HHLL
    elif a == 0x10:
      self.pc = hhll
    # Jx HHLL
    elif a == 0x12:
      if self.cond(x):
        self.pc == hhll
    # JME RX, RY, HHLL
    elif a == 0x13:
      if self.R[x] == self.R[y]:
        self.pc = hhll
    # CALL HHLL
    elif a == 0x14:
      self.pushStack(self.pc)
      self.sp =+ 2
      self.pc = hhll
    # RET
    elif a == 0x15:
      self.pc = self.popStack()
      self.sp =- 2
    # JMP RX
    elif a == 0x16:
      self.pc = self.R[x]
    # Cx HHLL
    elif a == 0x17:
      if self.cond(x):
        self.pushStack(self.pc)
        self.sp =+ 2
        self.pc = hhll
    # CALL Rx
    elif a == 0x18:
      self.pushStack(self.pc)
      self.sp =+ 2
      self.pc = self.R[x]
    # LDI RX, HHLL
    elif a == 0x20:
      self.R[x] = hhll
    # LDI SP, HHLL
    elif a == 0x21:
      self.sp = hhll
    # LDM RX, HHLL
    elif a == 0x22:
      self.R[x] = self.readMem(hhll)
    # LDM RX, RY
    elif a == 0x23:
      self.R[x] = self.readMem(R[y])
    # MOV RX, RY
    elif a == 0x24:
      self.R[x] = self.R[y]
    # STM RX, HHLL
    elif a == 0x30:
      self.writeMem(hhll,R[x])
    # STM RX, RY
      self.writemem(R[y],R[x])
    else:
      # Unknown
      self.log.warning('UNKNOWN OPCODE')
    return self.pc

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
