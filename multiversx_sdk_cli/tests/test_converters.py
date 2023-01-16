from multiversx_sdk_cli import utils


def test_str_to_hex_str():
    my_str = "1000000"
    hex_str = utils.str_int_to_hex_str(my_str)
    assert hex_str == "0f4240"

    my_str = "100000000000000000"
    hex_str = utils.str_int_to_hex_str(my_str)
    assert hex_str == "00016345785d8a0000"


def test_parse_keys():
    keys = "myKey,newKey,anotherKey"
    parsed_keys, num_keys = utils.parse_keys(keys)

    assert num_keys == 3
    assert parsed_keys == "@myKey@newKey@anotherKey"
