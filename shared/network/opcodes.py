from enum import IntEnum
from collections import namedtuple

class Opcodes(IntEnum):
    MSG_NULL = 0
    MSG_INITIAL_CONNECTION = 1
    CMSG_CAST_SPELL = 2
    CMSG_MOVE = 3
    SMSG_NOTIFICATION = 4
    SMSG_MOVE_OBJECT = 5
    SMSG_REMOVE_OBJECT = 6
    MSG_CHAT_MESSAGE = 7
    SMSG_ADD_OBJECT = 8
    CMSG_SPAWN_INGAME = 9

Opcode = namedtuple('Opcode', 'index name handler')

def defineOpcodes(table, null_handler):
    opTable = {}
    for name, handler in table:
        opcodeIndex = getattr(Opcodes, name).value
        opTable[opcodeIndex] = Opcode(opcodeIndex, name, handler)
    for opcode in Opcodes:
        if opcode.value not in opTable:
            print ('Assigning a NULL handler to %s.' % (opcode.name))
            opTable[opcode.value] = Opcode(opcode.value, opcode.name, null_handler)
    return opTable
