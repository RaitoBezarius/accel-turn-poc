from enum import IntEnum
from collections import namedtuple

class Opcodes(IntEnum):
    MSG_NULL = 0
    MSG_INITIAL_CONNECTION = 1
    MSG_CAST_SPELL = 2
    CMSG_MOVE = 3
    SMSG_NOTIFICATION = 4
    SMSG_MOVE_OBJECT = 5
    SMSG_REMOVE_SPELL = 6
    MSG_CHAT_MESSAGE = 7

Opcode = namedtuple('Opcode', 'index name handler')

def defineOpcodes(table):
    opTable = {}
    for name, handler in table:
        if not hasattr(Opcodes, name):
            raise RuntimeError("Missing opcode declaration.")

        opcodeIndex = getattr(Opcodes, name).value

        opTable[opcodeIndex] = Opcode(opcodeIndex, name, handler)
    return opTable
