# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import stsci_rtd_theme
import pathlib
import sys


sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'nexoclom2'
copyright = '2023, Matthew Burger'
author = 'Matthew Burger'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'autoapi.extension',
              'sphinx.ext.doctest',
              'sphinx.ext.mathjax',
              'sphinx.ext.duration',
              'sphinx.ext.autosummary',
              'myst_parser',
              'numpydoc',
              'sphinx.ext.napoleon']

autoapi_dirs = ['../../nexoclom2']

myst_enable_extensions = ["colon_fence",
                          'dollarmath',
                          'amsmath']
source_suffix = {'.rst': 'restructuredtext',
                 '.md': 'markdown'}

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'
# html_theme = 'stsci_rtd_theme'
# html_theme_path = [stsci_rtd_theme.get_html_theme_path()]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.7", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "markdown_it": ("https://markdown-it-py.readthedocs.io/en/latest", None),
}
