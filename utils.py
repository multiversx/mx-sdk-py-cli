import pathlib
import tarfile
import zipfile


def untar(arhive_path, destination_folder):
    ensure_folder(destination_folder)
    tar = tarfile.open(arhive_path)
    tar.extractall(path=destination_folder)
    tar.close()


def unzip(arhive_path, destination_folder):
    ensure_folder(destination_folder)
    with zipfile.ZipFile(arhive_path, "r") as my_zip:
        my_zip.extractall(destination_folder)


def ensure_folder(folder):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
