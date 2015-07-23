import struct

from functools import partial
from array import array

class Packet:

    integerFmt = {
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

    def __init__(self):
        self._id = None
        self.opcode = None
        self.content_size = None
        self.content = array('c')
        self.current_offset = 0

        self.header_serializer = struct.Struct('!QLQ')

        for integerType, fmt in self.integerFmt.items():
            for methodName in ("read", "write"):
                methodName += integerType.title()
                def doOperation(isRead, fmt, self, *args):
                    if isRead:
                        return self.read(fmt)
                    else:
                        return self.write(fmt, *args)

                methodObject = partial(doOperation,
                    methodName.startswith("read"),
                    fmt,
                    self)
                setattr(self, methodName, methodObject)

    def serialize(self):
        header = self.header_serializer.pack(self._id, self.opcode, self.content_size)
        return header + self.content.tostring()

    @staticmethod
    def construct(opcode):
        pckt = Packet()
        pckt._id = Packet.generate_seq_id()
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
        HEADER_FMT = '!QLQ'
        HEADER_SIZE = struct.calcsize(HEADER_FMT)

        if len(data) < HEADER_SIZE:
            return 0
        else:
            self._id, self.opcode, self.content_size = struct.unpack_from(HEADER_FMT, data)
            return HEADER_SIZE

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

    def writeString(self, string):
        self.writeUint32(len(string))
        self.write('!{}s'.format(len(string)), string)

    def read(self, fmt):
        offset = struct.calcsize(fmt)
        tpl = struct.unpack_from(fmt, self.content, self.current_offset)
        self.current_offset += offset
        return tpl

    def readString(self):
        size, = self.readUint32()
        string, = self.read('!{}s'.format(size))
        return string
