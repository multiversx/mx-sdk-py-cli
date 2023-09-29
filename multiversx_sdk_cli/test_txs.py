from multiversx_sdk_cli.cli import main as mxpy

unguarded_pem = "~/Desktop/Guardians/unguarded.pem"
alice = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

guarded = "~/Desktop/Guardians/address.pem"
guardian_address = "erd1nufxjweqjgk44drr49nxdnjc5ety288gd2hvvvm9tjkhlhgnnlusw2vmvt"
guardian = "~/Desktop/Guardians/guardian.pem"

guarded_keystore = "~/Desktop/Guardians/address_keystore.json"
passfile = "/home/alex/Desktop/Guardians/keystore_pass.txt"

service_guarded = "~/Desktop/Guardians/service_guarded.pem"
service_guardian = "erd16rq0gvkehwl4w5clh3np7352203spd8ts33ceuvxvtp84q0edfys65pquu"

chain = "1"
gas_limit = "500000000"
proxy = "https://express-api-up-mad.elrond.ro"
options = "2"
value = "1000000"

guardian_service_url = "https://mx-mfa-auth.elrond.ro/guardian"

unguarded_saved_tx = "/home/alex/Desktop/Guardians/unguarded_unsigned.json"
pem_guarded_saved_tx = "/home/alex/Desktop/Guardians/pem_guarded_unsigned.json"
service_guarded_saved_tx = "/home/alex/Desktop/Guardians/service_guarded_unsigned.json"


def unguarded_tx():
    mxpy([
        "tx",
        "new",
        "--pem",
        unguarded_pem,
        "--receiver",
        alice,
        "--recall-nonce",
        "--chain",
        chain,
        "--gas-limit",
        gas_limit,
        "--proxy",
        proxy,
        "--value",
        value,
        "--send"
    ])


def pem_gurded_tx():
    mxpy([
        "tx",
        "new",
        "--pem",
        guarded,
        "--receiver",
        alice,
        "--recall-nonce",
        "--chain",
        chain,
        "--gas-limit",
        gas_limit,
        "--proxy",
        proxy,
        "--options",
        options,
        "--value",
        value,
        "--guardian",
        guardian_address,
        "--guardian-pem",
        guardian,
        "--send"
    ])


def keystore_guarded_tx():
    mxpy([
        "tx",
        "new",
        "--keyfile",
        guarded_keystore,
        "--passfile",
        passfile,
        "--receiver",
        alice,
        "--recall-nonce",
        "--chain",
        chain,
        "--gas-limit",
        gas_limit,
        "--proxy",
        proxy,
        "--options",
        options,
        "--value",
        value,
        "--guardian",
        guardian_address,
        "--guardian-pem",
        guardian,
        "--send"
    ])


def service_guarded_tx(code: str):
    mxpy([
        "tx",
        "new",
        "--pem",
        service_guarded,
        "--receiver",
        alice,
        "--recall-nonce",
        "--chain",
        chain,
        "--gas-limit",
        gas_limit,
        "--proxy",
        proxy,
        "--options",
        options,
        "--value",
        value,
        "--guardian",
        service_guardian,
        "--guardian-service-url",
        guardian_service_url,
        "--guardian-2fa-code",
        code,
        "--send"
    ])


def cold_sign_unguarded():
    mxpy([
        "tx",
        "sign",
        "--pem",
        unguarded_pem,
        "--proxy",
        proxy,
        "--infile",
        unguarded_saved_tx
    ])


def cold_sign_pem_guarded():
    mxpy([
        "tx",
        "sign",
        "--pem",
        guarded,
        "--proxy",
        proxy,
        "--guardian",
        guardian_address,
        "--guardian-pem",
        guardian,
        "--infile",
        pem_guarded_saved_tx,
    ])


def cold_sign_keystore():
    mxpy([
        "tx",
        "sign",
        "--keyfile",
        guarded_keystore,
        "--passfile",
        passfile,
        "--proxy",
        proxy,
        "--guardian",
        guardian_address,
        "--guardian-pem",
        guardian,
        "--infile",
        pem_guarded_saved_tx
    ])


def cold_sign_service_guarded(code: str):
    mxpy([
        "tx",
        "sign",
        "--pem",
        service_guarded,
        "--proxy",
        proxy,
        "--guardian",
        service_guardian,
        "--guardian-service-url",
        guardian_service_url,
        "--guardian-2fa-code",
        code,
        "--infile",
        service_guarded_saved_tx
    ])


def main():
    # unguarded_tx()
    # pem_gurded_tx()
    # keystore_guarded_tx()
    # service_guarded_tx("895317")
    # cold_sign_unguarded()
    # cold_sign_pem_guarded()
    # cold_sign_keystore()
    # cold_sign_service_guarded("123456")
    pass


if __name__ == '__main__':
    main()
