# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import django
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../sslcommerz'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docs.django_settings')
django.setup()

# -- Project information -----------------------------------------------------
project = 'Django SSLCOMMERZ'
copyright = f'{datetime.now().year}, Django SSLCOMMERZ Contributors'
author = 'Django SSLCOMMERZ Contributors'

# The full version, including alpha/beta/rc tags
release = '1.0.0'
version = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.githubpages',
    'sphinxcontrib.httpdomain',
    'myst_parser',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Custom CSS
html_static_path = ['_static']
html_css_files = [
    'custom.css',
]

# Logo and favicon
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'

# -- Extension configuration -------------------------------------------------

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 'https://docs.djangoproject.com/en/stable/_objects/'),
    'drf': ('https://www.django-rest-framework.org/', None),
}

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Todo settings
todo_include_todos = True

# External links
extlinks = {
    'issue': ('https://github.com/your-username/django-sslcommerz/issues/%s', 'issue #%s'),
    'pr': ('https://github.com/your-username/django-sslcommerz/pull/%s', 'PR #%s'),
}

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files.
latex_documents = [
    ('index', 'django-sslcommerz.tex', 'Django SSLCOMMERZ Documentation',
     'Django SSLCOMMERZ Contributors', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    ('index', 'django-sslcommerz', 'Django SSLCOMMERZ Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    ('index', 'django-sslcommerz', 'Django SSLCOMMERZ Documentation',
     author, 'django-sslcommerz', 'Django integration package for SSLCOMMERZ Payment Gateway API v4.',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------
epub_title = project
epub_exclude_files = ['search.html']
