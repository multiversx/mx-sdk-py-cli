import shutil
import os
from os import path

from erdpy.templates.config import get_all_repositories


def list_templates():
    templates = []

    for repo in get_all_repositories():
        repo.download()
        templates.extend(repo.get_templates())
        
    templates = sorted(templates)
    print(templates)
