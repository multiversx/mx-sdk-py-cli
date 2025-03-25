from dataclasses import dataclass
from typing import Optional

from multiversx_sdk import Address

from multiversx_sdk_cli.interfaces import IAccount


@dataclass
class GuardianRelayerData:
    guardian: Optional[IAccount] = None
    guardian_address: Optional[Address] = None
    guardian_service_url: Optional[str] = None
    guardian_2fa_code: Optional[str] = None
    relayer: Optional[IAccount] = None
    relayer_address: Optional[Address] = None
