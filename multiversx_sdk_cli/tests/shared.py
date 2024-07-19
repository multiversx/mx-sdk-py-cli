import os
import shutil
from pathlib import Path

parent = Path(__file__).parent

SANDBOX = parent / "testdata-out/SANDBOX"
USERS = Path("~/multiversx-sdk/testwallets/latest/users")
VALIDATORS = Path("~/multiversx-sdk/testwallets/latest/validators")
DENOMINATION = "000000000000000000"
PROXY = "${PROXY:-http://localhost:7950}"
CHAIN_ID = "localnet"
TestUser = parent / "testdata/testUser.pem"
TestUser2 = parent / "testdata/testUser2.pem"
RUST_VERSION = "stable"


def clean_sandbox():
    if SANDBOX.is_dir():
        shutil.rmtree(SANDBOX)

    os.mkdir(SANDBOX)
