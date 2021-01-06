import binascii


class Converters:
    @staticmethod
    def str_int_to_hex_str(number_str: str) -> str:
        num_of_bytes = 1
        if len(number_str) > 2:
            num_of_bytes = int(len(number_str) / 2)
        int_str = int(number_str)
        int_bytes = int_str.to_bytes(num_of_bytes, byteorder="big")
        bytes_str = binascii.hexlify(int_bytes).decode()
        return bytes_str

    @staticmethod
    def parse_keys(bls_public_keys):
        keys = bls_public_keys.split(',')
        parsed_keys = ''
        for key in keys:
            parsed_keys += '@' + key
        return parsed_keys, len(keys)
