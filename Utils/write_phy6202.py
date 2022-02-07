#!/usr/bin/env python3

# wrflash_phy6202.py 07.12.2019 pvvx #

import serial;
import time;
import argparse
import os
import struct
import sys

START_BAUD = 115200
DEF_RUN_BAUD = 115200
MAX_FLASH_SIZE = 0x80000

PHY_FLASH_SECTOR_SIZE = 4096
PHY_FLASH_SECTOR_MASK = 0xfffff000
PHY_FLASH_ZONE = 0x4000

__version__ = "07.12.19"

class phyflasher:
	def __init__(self, port='COM1'):
		self.port = port
		self.baud = START_BAUD
		try:
			self._port = serial.Serial(self.port, self.baud)
			self._port.timeout = 1
		except:
			print ('Error: Open %s, %d baud!' % (self.port, self.baud))
			sys.exit(1)
	def SetAutoErase(self, enable = True):
		self.autoerase = enable
	def tstconnect(self):
		self._port.write(str.encode('getver '));
		read = self._port.read(6);
		if read == b'#ER>>:' :
			print ('PHY6202 - connected Ok')
			return True
		return False
	def SetBaud(self, baud):
		if self.baud != baud:
			print ('Reopen %s port %i baud...' % (self.port, baud), end = ' '),
			self._port.write(str.encode("uarts%i" % baud));
			self._port.timeout = 1
			read = self._port.read(3);
			if read == b'#OK':
				print ('ok')
				self._port.close()
				self.baud = baud
				self._port.baudrate = baud
				self._port.open();
			else:
				print ('error!')
				print ('Error set %i baud on %s port!' % (baud, self.port))
				self._port.close()
				sys.exit(3)
		return True			
	def Connect(self, baud=DEF_RUN_BAUD):
		self._port.setDTR(True) #TM   (lo)
		self._port.setRTS(True) #RSTN (lo)
		time.sleep(0.05)
		self._port.setDTR(False) #TM  (hi)
		self._port.flushOutput()
		self._port.flushInput()
		time.sleep(0.05)
		self._port.setRTS(False) #RSTN (hi)
		self._port.timeout = 0.1
		read = self._port.read(6);
		if read == b'cmd>>:' :
			print ('PHY6202 - Reset Ok')
			return self.SetBaud(baud)
		if self.tstconnect():
			return self.SetBaud(baud)
		print ('Error: device not connected on %s port!' % self.port)
		self._port.close()
		sys.exit(3)
	def cmd_era4k(self, offset):
		print ('Erase sector Flash at 0x%08x...' % offset, end = ' ')
		if offset < PHY_FLASH_ZONE:
			offset |= 0x400000
		self._port.write(str.encode('era4k %X' % offset)),
		tmp = self._port.timeout
		self._port.timeout = 0.5
		read = self._port.read(6)
		if read != b'#OK>>:':
			print ('error!')
			return False
		print ('ok')
		self._port.timeout = tmp
		return True
	def cmd_era32k(self, offset):
		print ('Erase block 32k Flash at 0x%08x...' % offset, end = ' '),
		if offset < PHY_FLASH_ZONE:
			offset |= 0x400000
		self._port.write(str.encode('er32k %X' % offset))
		tmp = self._port.timeout
		self._port.timeout = 1
		read = self._port.read(6)
		if read != b'#OK>>:':
			print ('error!')
			return False
		print ('ok')
		self._port.timeout = tmp
		return True
	def cmd_era64k(self, offset):
		print ('Erase block 64k Flash at 0x%08x...' % offset, end = ' '),
		self._port.write(str.encode('er64k %X' % offset))
		tmp = self._port.timeout
		self._port.timeout = 2
		read = self._port.read(6)
		if read != b'#OK>>:':
			print ('error!')
			return False
		print ('ok')
		self._port.timeout = tmp
		return True
	def cmd_er256(self, offset):
		print ('Erase block 256k Flash at 0x%08x...' % offset, end = ' '),
		self._port.write(str.encode('er256 %X' % offset))
		tmp = self._port.timeout
		self._port.timeout = 2
		read = self._port.read(6)
		if read != b'#OK>>:':
			print ('error!')
			return False
		print ('ok')
		self._port.timeout = tmp
		return True
	def cmd_er512(self, offset):
		print ('Erase block 512k Flash at 0x%08x...' % offset, end = ' '),
		self._port.write(str.encode('er512 %X' % offset))
		tmp = self._port.timeout
		self._port.timeout = 3
		read = self._port.read(6)
		if read != b'#OK>>:':
			print ('error!')
			return False
		print ('ok')
		self._port.timeout = tmp
		return True
	def cmd_erase_all_chipf(self):
		print ('Erase All Chip Flash...', end = ' '),
		self._port.write(str.encode('chipf '))
		tmp = self._port.timeout
		self._port.timeout = 7
		read = self._port.read(6)
		if read != b'#OK>>:':
			print ('error!')
			return False
		print ('ok')
		self._port.timeout = tmp
		return True
	def EraseSectorsFlash(self, offset = 0, size = MAX_FLASH_SIZE):
		count = (size + PHY_FLASH_SECTOR_SIZE - 1) / PHY_FLASH_SECTOR_SIZE
		offset &= PHY_FLASH_SECTOR_MASK
		if offset==0 and size == MAX_FLASH_SIZE:
			if not self.cmd_erase_all_chipf():
				return False
			return True
		if count > 0 and count < 0x10000 and offset >= 0: # 1 byte .. 16 Mbytes
			while count > 0:
				if (offset & 0x7FFFF) == 0 and count > 127:
					if not self.cmd_er512(offset):
						return False
					offset += 0x80000
					count-=128
				elif (offset & 0x3FFFF) == 0 and count > 63:
					if not self.cmd_er256(offset):
						return False
					offset += 0x40000
					count-=64
				elif (offset & 0x0FFFF) == 0 and count > 15:
					if not self.cmd_era64k(offset):
						return False
					offset += 0x10000
					count-=16
				elif (offset & 0x07FFF) == 0 and count > 7:
					if not self.cmd_era32k(offset):
						return False
					offset += 0x8000
					count-=8
				else:
					if not self.cmd_era4k(offset):
						return False
					offset += PHY_FLASH_SECTOR_SIZE
					count-=1
		else:
			return False
		return True
	def send_blk(self, stream, offset, size, blkcnt, blknum):
		self._port.timeout = 1
		print ('Write 0x%08x bytes to Flash at 0x%08x...' % (size, offset), end = ' '),
		if blknum == 0:  
			self._port.write(str.encode('cpnum %d ' % blkcnt))
			read = self._port.read(6)
			if read != b'#OK>>:':
				print ('error!')
				return False
		self._port.write(str.encode('cpbin %d %X %X %X' % (blknum, offset, size, 0x1FFF0000+offset)))
		read = self._port.read(13)
		if read != b'by hex mode: ':
			print ('error!')
			return False
		data = stream.read(size)
		self._port.write(data)
		read = self._port.read(23); #'checksum is: 0x00001d1e'
		#print ('%s' % read),
		if read[0:15] != b'checksum is: 0x':
			print ('error!')
			return False
		self._port.write(read[15:])
		read = self._port.read(6)
		if read != b'#OK>>:':
			print ('error!')
			return False
		print ('ok')
		return True
	def WriteBlockFlash(self, stream, offset = 0, size = 0x8000):
		offset &= 0x00ffffff
		if self.autoerase:
			if not self.EraseSectorsFlash(offset, size):	
				return False
		sblk = 0x8000
		blkcount = (size + sblk - 1) / sblk
		blknum = 0
		while(size > 0):
			if size < sblk:
				sblk = size
			if not self.send_blk(stream, offset, sblk, blkcount, blknum):
				return False
			blknum+=1
			offset+=sblk
			size-=sblk
		return True
	def WriteResFlash(self, stream, offset, size):
		while(size > 0):
#			if self.autoerase:
			if not self.cmd_era4k(offset & PHY_FLASH_SECTOR_MASK):
				return False
			end_sector = (offset & PHY_FLASH_SECTOR_MASK) + PHY_FLASH_SECTOR_SIZE
			sblk = end_sector - offset
			print ('Write 0x%08x bytes to Flash at 0x%08x...' % (sblk, offset), end = ' '),
			while(offset < end_sector):
				dwx, = struct.unpack('<I', stream.read(4))
				if dwx != 0xffffffff:
					self._port.write(str.encode('write%X %X' % (offset, dwx)))
					read = self._port.read(6)
					if read != b'#OK>>:':
						print ('error!')
						return False
				offset+=4
			print ('ok')				
			size -= sblk
		return True

class FatalError(RuntimeError):
	def __init__(self, message):
		RuntimeError.__init__(self, message)

	@staticmethod
	def WithResult(message, result):
		message += " (result was %s)" % hexify(result)
		return FatalError(message)

def arg_auto_int(x):
	return int(x, 0)

def main():
	parser = argparse.ArgumentParser(description='WrFlash-PHY6202 Utility version %s' % __version__, prog='WrFlash_phy6202')
	parser.add_argument('--port', '-p', help='Serial port device',	default='COM1');
	parser.add_argument('--baud', '-b',	help='Set Port Baud (115200, 250000, 500000, 1000000)',	type=arg_auto_int, default=DEF_RUN_BAUD);
	parser.add_argument('--chiperase', '-c',  action='store_true', help='All Chip Erase');
	parser.add_argument('address', help='Start Flash address', type=arg_auto_int)
	parser.add_argument('filename', help='File name')
	
	args = parser.parse_args()

	print('WrFlash-PHY6202 Utility version %s' % __version__)

	phy = phyflasher(args.port)
	print ('Connecting...')
	if phy.Connect(args.baud):
		stream = open(args.filename, 'rb')
		size = os.path.getsize(args.filename)
		if size < 1:
			stream.close
			print ('Error: File size = 0!')
			sys.exit(1)
		offset = args.address & 0x00ffffff
		if size+offset > MAX_FLASH_SIZE:
			size = MAX_FLASH_SIZE - offset
		if size < 1:
			stream.close
			print ('Error: Write File size = 0!')
			sys.exit(1)
		ssize = size
		if args.chiperase == True:
			if not phy.cmd_erase_all_chipf():
				stream.close
				print ('Error: Clear Flash!')
				sys.exit(2)
		phy.SetAutoErase(not args.chiperase)
		print ('Write Flash data 0x%08x to 0x%08x from file: %s ...' % (offset, offset + size, args.filename))
		start = offset
		if offset < PHY_FLASH_ZONE:
			sblk = PHY_FLASH_ZONE - offset
			stream.seek(sblk, 0)
			size-=sblk
			offset+=sblk
		if size > 0:
			if not phy.WriteBlockFlash(stream, offset, size):
				stream.close
				print ('Error: Write Flash!')
				sys.exit(2)
		if start < PHY_FLASH_ZONE:
			stream.seek(0, 0)
			if not phy.WriteResFlash(stream, start, sblk):
				stream.close
				print ('Error: Write Flash!')
				sys.exit(2)
		stream.close
		print ('--------------------------------------------------------')
		print ('Write Flash data 0x%08x to 0x%08x from file: %s - ok.' % (start, start + ssize, args.filename))
	sys.exit(0)	

if __name__ == '__main__':
	main()
