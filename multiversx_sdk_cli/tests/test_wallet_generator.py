from pathlib import Path
from multiversx_sdk_cli.cli import main

def test_generate_wallet():
    result = main(['wallet', 'new'])
    
    if not result:
        assert True
    else:
        assert False


def test_generate_wallet_and_save_in_pem_format():
    output_path = Path(__file__).parent / "testdata-out" / "testWallet.pem"
    result = main(['wallet', 'new', '--pem', '--output-path', str(output_path)])
    
    assert Path.is_file(output_path) == True

    if not result:
        assert True
    else:
        assert False


def test_derive_pem_from_mnemonic(monkeypatch):
    output_path = Path(__file__).parent / "testdata-out" / "wallet.pem"
    test_mnemonic = "moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve"
    monkeypatch.setattr('builtins.input', lambda _: test_mnemonic)

    result = main(['wallet', 'derive', str(output_path), '--mnemonic'])
    assert Path.is_file(output_path) == True

    if not result:
        assert True
    else:
        assert False
