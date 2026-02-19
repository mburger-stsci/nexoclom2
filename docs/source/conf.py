# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import stsci_rtd_theme
import pathlib
import sys
import sphinx
import os
from docs.conf import autoclass_content
from packaging.version import Version



def setup(app):
    app.add_css_file("stsci.css")


sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# MyST theme
# https://pypi.org/project/stsci-rtd-theme/

project = 'nexoclom2'
copyright = '2025, Matthew Burger'
author = 'Matthew Burger'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              # 'autoapi.extension',
              'sphinx.ext.doctest',
              'sphinx.ext.mathjax',
              'sphinx.ext.duration',
              'myst_parser',
              'numpydoc.numpydoc',
              'sphinx.ext.napoleon']
              # 'sphinxcontrib.napoleon']

autoapi_dirs = ['../../nexoclom2']

napoleon_include_special_with_doc = False
napoleon_include_private_with_doc = False

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    extensions.append('sphinx.ext.mathjax')
elif Version(sphinx.__version__) < Version('1.4'):
    extensions.append('sphinx.ext.pngmath')
else:
    extensions.append('sphinx.ext.imgmath')


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
# html_theme = 'sphinx_rtd_theme'
html_theme = 'stsci_rtd_theme'
html_theme_path = [stsci_rtd_theme.get_html_theme_path()]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.13", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "markdown_it": ("https://markdown-it-py.readthedocs.io/en/latest", None),
}

autodoc_default_options = {'special-members': None}

#autoclass_content = 'init'
numpydoc_use_plots = True
numpydoc_show_class_members = False
