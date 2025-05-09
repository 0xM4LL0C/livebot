import os
from functools import partial

from markdown.extensions.toc import TocExtension
from mkdocs.config.defaults import MkDocsConfig
from slugify import slugify


def on_pre_build(config: MkDocsConfig):
    os.system("python3 tools/update_docs.py")


def on_config(config: MkDocsConfig):
    config["markdown_extensions"].append(
        TocExtension(slugify=partial(slugify, allow_unicode=True)),
    )
    return config
