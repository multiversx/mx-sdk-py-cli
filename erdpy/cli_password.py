from getpass import getpass

def load_password(args):
    if args.passfile:
        with open(args.passfile) as pass_file:
            return pass_file.read().strip()
    return getpass("Keyfile's password: ")
