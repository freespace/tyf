# -*- coding:utf-8 -*-
__copyright__ = "Copyright © 2012-2015, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html"
__author__    = "THOORENS Bruno"
__tiff__      = (6,0)
__geotiff__   = (1,8,1)

import io, os, sys, struct, collections

unpack = lambda fmt, fileobj: struct.unpack(fmt, fileobj.read(struct.calcsize(fmt)))
pack = lambda fmt, fileobj, value: fileobj.write(struct.pack(fmt, *value))

TYPES = {
	1:  ("B",  "UCHAR or USHORT"),
	2:  ("c",  "ASCII"),
	3:  ("H",  "UBYTE"),
	4:  ("L",  "ULONG"),
	5:  ("LL", "URATIONAL"),
	6:  ("b",  "CHAR or SHORT"),
	7:  ("c",  "UNDEFINED"),
	8:  ("h",  "BYTE"),
	9:  ("l",  "LONG"),
	10: ("ll", "RATIONAL"),
	11: ("f",  "FLOAT"),
	12: ("d"   "DOUBLE"),
}

# assure compatibility python 2 & 3
if sys.version_info[0] >= 3:
	from io import BytesIO as StringIO
	TYPES[2] = ("s", "ASCII")
	TYPES[7] = ("s", "UDEFINED")
	import functools
	reduce = functools.reduce
	long = int
else:
	from StringIO import StringIO
	reduce = __builtins__["reduce"]

from . import ifd, gkd


def _read_IFD(obj, fileobj, offset, byteorder="<"):
	# fileobj seek must be is on the start offset
	fileobj.seek(offset)
	# get number of entry
	nb_entry, = unpack(byteorder+"H", fileobj)

	# for each entry 
	for i in range(nb_entry):
		# read tag, type and cound values
		tag, typ, count = unpack(byteorder+"HHL", fileobj)
		# extract data
		data = fileobj.read(struct.calcsize("L"))
		if not isinstance(data, bytes):
			data = data.encode()
		_typ = TYPES[typ][0]

		# create a tifftag
		tt = ifd.TiffTag(tag)
		# initialize what we already know
		tt.type = typ
		tt.count = count
		# to know if ifd entry value is an offset
		tt._determine_if_offset()

		# if value is offset
		if tt.value_is_offset:
			# read offset value
			value, = struct.unpack(byteorder+"L", data)
			fmt = byteorder + _typ*count
			bckp = fileobj.tell()
			# go to offset in the file
			fileobj.seek(value)
			# if ascii type, convert to bytes
			if typ == 2: tt.value = b"".join(e for e in unpack(fmt, fileobj))
			# else if undefined type, read data
			elif typ == 7: tt.value = fileobj.read(count)
			# else unpack data
			else: tt.value = unpack(fmt, fileobj)
			# go back to ifd entry
			fileobj.seek(bckp)

		# if value is in the ifd entry
		else:
			if typ in [2, 7]:
				tt.value = data[:count]
			else:
				fmt = byteorder + _typ*count
				tt.value = struct.unpack(fmt, data[:count*struct.calcsize(_typ)])

		obj.addtag(tt)

def from_buffer(obj, fileobj, offset, byteorder="<"):
	# read data from offset
	_read_IFD(obj, fileobj, offset, byteorder)
	# get next ifd offset
	next_ifd, = unpack(byteorder+"L", fileobj)

	## read private ifd if any
	# Exif IFD
	if 34665 in obj:
		obj.private_ifd[34665] = ifd.Ifd(tagname="Exif tag")
		_read_IFD(obj.private_ifd[34665], fileobj, obj[34665], byteorder)
	# GPS IFD
	if 34853 in obj:
		obj.private_ifd[34853] = ifd.Ifd(tagname="GPS tag")
		_read_IFD(obj.private_ifd[34853], fileobj, obj[34853], byteorder)

	## read raster data if any
	# striped raster data
	if 273 in obj:
		for offset,bytecount in zip(obj[273], obj[279]):
			fileobj.seek(offset)
			obj.stripes += (fileobj.read(bytecount), )
	# free raster data
	elif 288 in obj:
		for offset,bytecount in zip(obj[288], obj[289]):
			fileobj.seek(offset)
			obj.free += (fileobj.read(bytecount), )
	# tiled raster data
	elif 324 in obj:
		for offset,bytecount in zip(obj[324], obj[325]):
			fileobj.seek(offset)
			obj.tiles += (fileobj.read(bytecount), )
	# get interExchange (thumbnail data for JPEG/EXIF data)
	if 513 in obj:
		fileobj.seek(obj[513])
		obj.jpegIF = fileobj.read(obj[514])

	return next_ifd

def _write_IFD(obj, fileobj, offset, byteorder="<"):
	# go where obj have to be written
	fileobj.seek(offset)
	# sort data to be writen
	tags = sorted(list(dict.values(obj)), key=lambda e:e.tag)
	# write number of entries
	pack(byteorder+"H", fileobj, (len(tags),))

	first_entry_offset = fileobj.tell()
	# write all ifd entries
	for t in tags:
		# write tag, type & count
		pack(byteorder+"HHL", fileobj, (t.tag, t.type, t.count))

		# if value is not an offset
		if not t.value_is_offset:
			value = t._fill()
			n = len(value)
			if sys.version_info[0] >= 3 and t.type in [2, 7]:
				fmt = str(n)+TYPES[t.type][0]
				value = (value,)
			else:
				fmt = n*TYPES[t.type][0]
			pack(byteorder+fmt, fileobj, value)
		else:
			pack(byteorder+"L", fileobj, (0,))

	next_ifd_offset = fileobj.tell()
	pack(byteorder+"L", fileobj, (0,))

	# prepare jumps
	data_offset = fileobj.tell()
	step1 = struct.calcsize("HHLL")
	step2 = struct.calcsize("HHL")

	# comme back to first ifd entry
	fileobj.seek(first_entry_offset)
	for t in tags:
		# for each tag witch value needs offset
		if t.value_is_offset:
			# go to offset value location (jump over tag, type, count)
			fileobj.seek(step2, 1)
			# write offset where value is about to be stored
			pack(byteorder+"L", fileobj, (data_offset,))
			# remember where i am in ifd entries
			bckp = fileobj.tell()
			# go to offset where value is about to be stored
			fileobj.seek(data_offset)
			# prepare value according to python version
			if sys.version_info[0] >= 3 and t.type in [2, 7]:
				fmt = str(t.count)+TYPES[t.type][0]
				value = (t.value,)
			else:
				fmt = t.count*TYPES[t.type][0]
				value = t.value
			# write value
			pack(byteorder+fmt, fileobj, value)
			# remmember where to put next value
			data_offset = fileobj.tell()
			# go to where I was in ifd entries
			fileobj.seek(bckp)
			lastt = t #
		else:
			fileobj.seek(step1, 1)

	return next_ifd_offset

def to_buffer(obj, fileobj, offset, byteorder="<"):
	size = obj.size

	raw_offset = offset + size["ifd"] + size["data"]
	# add GPS and Exif IFD sizes...
	for tag, p_ifd in sorted(obj.private_ifd.items(), key=lambda e:e[0]):
		obj.set(tag, 4, 1, raw_offset)
		size = p_ifd.size
		raw_offset = raw_offset + size["ifd"] + size["data"]

	# knowing where raw image have to be writen, update [Strip/Free/Tile]Offsets
	if 273 in obj:
		_279 = obj[279]
		stripoffsets = (raw_offset,)
		for bytecount in _279[:-1]:
			stripoffsets += (stripoffsets[-1]+bytecount, )
		obj.set(273, 4, len(stripoffsets), stripoffsets)
		next_ifd = stripoffsets[-1] + _279[-1]
	elif 288 in obj:
		_289 = obj[289]
		freeoffsets = (raw_offset,)
		for bytecount in _289[:-1]:
			freeoffsets += (freeoffsets[-1]+bytecount, )
		obj.set(288, 4, len(freeoffsets), freeoffsets)
		next_ifd = freeoffsets[-1] + _289[-1]
	elif 324 in obj:
		_325 = obj[325]
		tileoffsets = (raw_offset,)
		for bytecount in _325[:-1]:
			tileoffsets += (tileoffsets[-1]+bytecount, )
		obj.set(324, 4, len(tileoffsets), tileoffsets)
		next_ifd = tileoffsets[-1] + _325[-1]
	elif 513 in obj:
		interexchangeoffset = raw_offset
		obj.set(513, 4, 1, raw_offset)
		next_ifd = interexchangeoffset + obj[514]
	else:
		next_ifd = raw_offset

	next_ifd_offset = _write_IFD(obj, fileobj, offset, byteorder)
	# write "Exif IFD" and "GPS IFD"
	for tag, p_ifd in sorted(obj.private_ifd.items(), key=lambda e:e[0]):
		_write_IFD(p_ifd, fileobj, obj[tag], byteorder)

	# write raw data
	if len(obj.stripes):
		for offset,data in zip(obj[273], obj.stripes):
			fileobj.seek(offset)
			fileobj.write(data)
	elif len(obj.free):
		for offset,data in zip(obj[288], obj.stripes):
			fileobj.seek(offset)
			fileobj.write(data)
	elif len(obj.tiles):
		for offset,data in zip(obj[324], obj.tiles):
			fileobj.seek(offset)
			fileobj.write(data)
	elif obj.jpegIF != b"":
		fileobj.seek(obj[513])
		fileobj.write(obj.jpegIF)

	fileobj.seek(next_ifd_offset)
	return next_ifd


class TiffFile(list):

	gkd = property(lambda obj: [gkd.Gkd(ifd) for ifd in obj], None, None, "list of geotiff directory")

	def __init__(self, fileobj, byteorder=0x4949):
		byteorder = "<" if byteorder == 0x4949 else ">"

		fileobj.seek(2)
		magic_number, = unpack(byteorder+"H", fileobj)
		if magic_number != 0x2A: # 42
			fileobj.close()
			raise IOError("Bad magic number. Not a valid TIFF file")
		next_ifd, = unpack(byteorder+"L", fileobj)

		ifds = []
		while next_ifd != 0:
			i = ifd.Ifd("private")
			next_ifd = from_buffer(i, fileobj, next_ifd, byteorder)
			ifds.append(i)

		fileobj.close()
		list.__init__(self, ifds)

	def __getitem__(self, item):
		if isinstance(item, tuple): return list.__getitem__(self, item[0])[item[-1]]
		else: return list.__getitem__(self, item)

	def __add__(self, value):
		if isinstance(value, JpegFile):
			for i in value: self.append(i)
		elif isinstance(value, ifd.Ifd):
			self.append(value)
		return self

	def save(self, f, byteorder="<"):
		if hasattr(f, "close"): out = f
		else: out = io.open(f, "wb")
		pack(byteorder+"HH", out, (0x4949 if byteorder == "<" else 0x4d4d, 0x2A,))
		next_ifd = 8
		for i in self:
			pack(byteorder+"L", out, (next_ifd,))
			next_ifd = to_buffer(i, out, next_ifd, byteorder)
		if not isinstance(out, StringIO): out.close()


class JpegFile(collections.OrderedDict):

	jfif = property(lambda obj: collections.OrderedDict.__getitem__(obj, 0xffe0), None, None, "JFIF data")
	thumbnail = property(lambda obj: collections.OrderedDict.__getitem__(obj, 0xffe1)[-1].jpegIF, None, None, "Thumbnail data")
	exif = property(lambda obj: collections.OrderedDict.__getitem__(obj, 0xffe1)[0], None, None, "Exif data")

	def __init__(self, fileobj):
		markers = collections.OrderedDict()
		marker, = unpack(">H", fileobj)
		while marker != 0xffd9: # EOI (End Of Image) Marker
			marker, count = unpack(">HH", fileobj)
			# here is raster data marker, copy all after marker id
			if marker == 0xffda:
				fileobj.seek(-2, 1)
				markers[0xffda] = fileobj.read()
				# say it is the end of the file
				marker = 0xffd9
			elif marker == 0xffe1:
				string = StringIO(fileobj.read(count-2)[6:])
				first, = unpack(">H", string)
				string.seek(0)
				markers[marker] = TiffFile(string, first)
			else:
				markers[marker] = fileobj.read(count-2)

		fileobj.close()
		collections.OrderedDict.__init__(self, markers)

	def __getitem__(self, item):
		try: return collections.OrderedDict.__getitem__(self, 0xffe1)[0,item]
		except KeyError: return collections.OrderedDict.__getitem__(self, item)

	def _pack(self, marker, fileobj):
		data = self[marker]
		if marker == 0xffda:
			pack(">H", fileobj, (marker,))
		elif marker == 0xffe1:
			string = StringIO()
			self[marker].save(string)
			data = b"Exif\x00\x00" + string.getvalue()
			pack(">HH", fileobj, (marker, len(data) + 2))
		else:
			pack(">HH", fileobj, (marker, len(data) + 2))
		fileobj.write(data)

	def save(self, f):
		if hasattr(f, "close"): out = f
		else: out = io.open(f, "wb")
		pack(">H", out, (0xffd8,))
		for key in self: self._pack(key, out)
		pack(">H", out, (0xffd9,))
		if not isinstance(out, StringIO): out.close()


def open(f):
	if hasattr(f, "close"): fileobj = f
	else: fileobj = io.open(f, "rb")
		
	first, = unpack(">H", fileobj)
	fileobj.seek(0)

	if first == 0xffd8:
		return JpegFile(fileobj)

	elif first in [0x4d4d, 0x4949]:
		return TiffFile(fileobj, first)
