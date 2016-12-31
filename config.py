# Configuration file for docbrowser.py

import os

mounts = [
  {
    'name': 'Example Documentation',
    'slug': 'example',           # optional, fallback on 'name'
    'path': os.path.join(os.path.dirname(__file__), 'example'),
    'index_redirect': 'latest',
    'index_file': 'index.html',  # default
    'aliases': {                 # optional
      'latest': 'v1.0.1',
      'stable': 'v1.0.0'
    }
  }
]
