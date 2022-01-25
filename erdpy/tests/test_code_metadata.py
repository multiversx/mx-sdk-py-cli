from erdpy.contracts import CodeMetadata

def test_code_metadata_defaults():
    assert CodeMetadata().to_hex() == "0500"
    assert CodeMetadata().to_hex() == CodeMetadata(upgradeable=True, readable=True, payable=False, payable_by_sc=False).to_hex()

def test_code_metadata_single_flag():
    assert CodeMetadata(upgradeable=False, readable=False, payable=False, payable_by_sc=False).to_hex() == "0000"
    assert CodeMetadata(upgradeable=True, readable=False, payable=False, payable_by_sc=False).to_hex() == "0100"
    assert CodeMetadata(upgradeable=False, readable=True, payable=False, payable_by_sc=False).to_hex() == "0400"
    assert CodeMetadata(upgradeable=False, readable=False, payable=True, payable_by_sc=False).to_hex() == "0002"
    assert CodeMetadata(upgradeable=False, readable=False, payable=False, payable_by_sc=True).to_hex() == "0004"

def test_code_metadata_multiple_flags():
    assert CodeMetadata(upgradeable=False, readable=True, payable=False, payable_by_sc=True).to_hex() == "0404"
    assert CodeMetadata(upgradeable=True, readable=True, payable=False, payable_by_sc=False).to_hex() == "0500"
    assert CodeMetadata(upgradeable=False, readable=False, payable=True, payable_by_sc=True).to_hex() == "0006"
    assert CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_sc=True).to_hex() == "0506"
