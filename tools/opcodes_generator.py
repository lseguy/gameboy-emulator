import argparse
import json


def to_dict_entry(value: int, json_object: dict) -> str:
    hex_repr = f'0x{value:02x}'
    return (
        f"{hex_repr}: CPUInstruction(\n"
        f"    name='{json_object['Name']}\',\n"
        f"    length={json_object['Length']},\n"
        f"    cycles_no_branch={json_object['TCyclesNoBranch']},\n"
        f"    cycles_branch={json_object['TCyclesBranch']},\n"
        f"    opcode={hex_repr},\n"
        f"),"
    )


def process_file(filename: str) -> None:
    with open(filename) as f:
        data = json.load(f)

    for i, instruction in enumerate(data['Unprefixed']):
        entry = to_dict_entry(i, instruction)
        print(entry)

    for i, instruction in enumerate(data['CBPrefixed']):
        value = (0xcb << 8) + i
        entry = to_dict_entry(value, instruction)
        print(entry)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates boilerplate code for opcodes.')
    parser.add_argument('filename', help='the path of the JSON file containing the opcode definitions')
    args = parser.parse_args()

    process_file(args.filename)
