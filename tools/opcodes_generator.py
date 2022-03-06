import json


def to_opcode_definition(value: bytes, json_object: dict):
    bytes_literal = ''.join([f'\\x{byte:02x}' for byte in value])
    return (
        f"b'{bytes_literal}': OpCode(name='{json_object['Name']}\', "
        f"length={json_object['Length']}, "
        f"code=b'{bytes_literal}'"
        f"),"
    )


def read_file(filename):
    with open(filename) as f:
        data = json.load(f)

    for i, instruction in enumerate(data['Unprefixed']):
        value = i.to_bytes(1, byteorder='little')
        opcode = to_opcode_definition(value, instruction)
        print(opcode)

    for i, instruction in enumerate(data['CBPrefixed']):
        value = b'\xcb' + i.to_bytes(1, byteorder='little')
        opcode = to_opcode_definition(value, instruction)
        print(opcode)


if __name__ == '__main__':
    read_file('data/dmgops.json')
