# Configuration file for docbrowser.py

import os
from docbrowser import Mount

address = 'localhost:8000'
debug = False

mounts = [
  Mount(
    name = 'Example Documentation',
    slug = 'example',
    path = os.path.join(os.path.dirname(__file__), 'example')
  )
]
