import struct
import time

from functools import partial
from array import array

class Packet:

    convenienceFmt = {
        "int8": "!b",
        "int16": "!h",
        "int32": "!i",
        "int64": "!q",
        "uint8": "!B",
        "uint16": "!H",
        "uint32": "!I",
        "uint64": "!Q",
        "float": "!f",
        "double": "!d",
        "bool": "!?"
    }

    seq_id = 0
    HeaderSize = struct.calcsize('!QLdQ')
    HeaderFmt = '!QLdQ'

    def __init__(self):
        self._id = None
        self.opcode = None
        self.time = None
        self.content_size = None
        self.content = array('c')
        self.current_offset = 0

        self.header_serializer = struct.Struct(self.HeaderFmt)

        for fieldType, fmt in self.convenienceFmt.items():
            for methodName in ("read", "write", "canRead"):
                methodName += fieldType.title()
                def doOperation(methodType, fmt, self, *args):
                    if methodType.startswith("read"):
                        value, = self.read(fmt)
                        return value
                    elif methodType.startswith("write"):
                        add_fmt = fmt[1] * (len(args) - 1)
                        fmt += add_fmt
                        return self.write(fmt, *args)
                    else:
                        size = struct.calcsize(fmt)
                        return (self.content_size - self.current_offset) >= size

                methodObject = partial(doOperation,
                    methodName,
                    fmt,
                    self)
                setattr(self, methodName, methodObject)

    def serialize(self):
        header = self.header_serializer.pack(self._id, self.opcode, self.time, self.content_size)
        return header + self.content.tostring()

    @staticmethod
    def construct(opcode):
        pckt = Packet()
        pckt._id = Packet.generate_seq_id()
        pckt.time = time.time()
        pckt.opcode = opcode
        pckt.content_size = 0
        return pckt

    @classmethod
    def generate_seq_id(cls):
        cls.seq_id += 1
        return cls.seq_id

    def isHeaderComplete(self):
        return (self.content_size is not None)

    def isComplete(self):
        return (self.content_size is not None) and (len(self.content) == self.content_size)

    def consumeHeader(self, data):
        if len(data) < self.HeaderSize:
            return 0
        else:
            self._id, self.opcode, self.time, self.content_size = struct.unpack_from(self.HeaderFmt, data)
            return self.HeaderSize

    def consumeContent(self, data):
        size_expected = self.content_size - len(self.content)
        content = data[:size_expected]
        self.content.extend(content)
        return len(content)

    def resetReadPos(self):
        self.current_offset = 0

    def write(self, fmt, *values):
        offset = struct.calcsize(fmt)
        self.content.extend('\0' * offset)
        struct.pack_into(fmt, self.content, self.content_size, *values)
        self.content_size += offset

    def writeString(self, *strings):
        for string in strings:
            self.writeUint32(len(string))
            self.write('!{}s'.format(len(string)), string)

    def writeVector(self, *vectors):
        for vector in vectors:
            if isinstance(vector.x, int):
                self.writeInt32(vector.x, vector.y)
            elif isinstance(vector.x, float):
                self.writeFloat(vector.x, vector.y)

    def read(self, fmt):
        offset = struct.calcsize(fmt)
        tpl = struct.unpack_from(fmt, self.content, self.current_offset)
        self.current_offset += offset
        return tpl

    def readString(self):
        size = self.readUint32()
        string, = self.read('!{}s'.format(size))
        return string

    def skipBytes(self, n_bytes):
        self.current_offset += n_bytes

    def skip(self, fmt):
        self.skipBytes(struct.calcsize(fmt))
