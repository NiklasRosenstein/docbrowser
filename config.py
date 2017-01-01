# Configuration file for docbrowser.py

import os

html_parser = 'lxml'
html_formatter = 'minimal'
mounts = [
  {
    'name': 'Example Documentation',
    'slug': 'example',                         # optional, fallback on 'name'
    'path': os.path.join(os.path.dirname(__file__), 'example'),
    'index_redirect': 'latest',
    'version_sort': (lambda v1, v2: v1 < v2), # default
    'index_file': 'index.html',               # default
    'aliases': {                              # optional
      'latest': lambda v: v[-1],
      'stable': 'v1.0.0'
    }
  }
]
