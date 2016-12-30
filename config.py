# Configuration file for docbrowser.py

import os

mounts = {
  'example': {
    'path': os.path.join(os.path.dirname(__file__), 'example'),
    'aliases': {
      'latest': 'v1.0.1',
      'stable': 'v1.0.0'
    }
  }
}
