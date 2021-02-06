# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Safe Chicken'
copyright = '2021, Claudio Nold'
author = 'Claudio Nold'

# The full version, including alpha/beta/rc tags
release = '0.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'sphinx.ext.extlinks',
    'sphinx.ext.autodoc',
    'sphinxcontrib.blockdiag',
    'sphinxcontrib.plantuml',
    'sphinx_rtd_theme'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']



# blockdiag

# Fontpath for blockdiag (truetype font)
# blockdiag_fontpath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
blockdiag_antialias = True
blockdiag_transparency = True
blockdiag_html_image_format = "SVG"


# seqdiag
# seqdiag_fontpath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
seqdiag_antialias = True
seqdiag_transparency = True
seqdiag_html_image_format = "SVG"

# -- todo
todo_include_todos = True

# -- for Read the Docs autobuild process
master_doc = 'index'
