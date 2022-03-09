def read_binary_file(filename: str) -> bytes:
    with open(filename, 'rb') as f:
        return f.read()
