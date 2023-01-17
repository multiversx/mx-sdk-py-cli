from pathlib import Path

from multiversx_sdk_cli.projects.constants import (OLD_PROJECT_CONFIG_FILENAME,
                                                   PROJECT_CONFIG_FILENAME)


def migrate_project_config_file(project_path: Path):
    new_config_file = project_path / PROJECT_CONFIG_FILENAME
    old_config_file = project_path / OLD_PROJECT_CONFIG_FILENAME

    if old_config_file.exists():
        if new_config_file.exists():
            old_config_file.unlink()
        else:
            old_config_file.rename(new_config_file)


def migrate_project_templates(parent_folder: Path):
    for project_folder in parent_folder.iterdir():
        if project_folder.is_dir():
            migrate_project_config_file(project_folder)
