# Configuration file for docbrowser.py

import os

mounts = [
  {
    'name': 'Example Documentation',
    'slug': 'example',
    'path': os.path.join(os.path.dirname(__file__), 'example'),
    'index_redirect': 'latest',
    'aliases': {
      'latest': 'v1.0.1',
      'stable': 'v1.0.0'
    }
  }
]
