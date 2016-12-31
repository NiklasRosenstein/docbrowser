# docbrowser

Docbrowser is a simple Python web application that serves static content, such
as API documentation, and inserts a header that allows to switch between
different versions of the documentation.

__Requirements__

- Python
- Flask

To run Docbrowser, use `python run.py` (your choice of Python 2 or 3).

__Configuration__

Edit `config.py` to configure Docbrowser. The default configuration is included
below for reference.

```python
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
```

---

<p align="center">Copyright &copy; 2017 &ndash; Niklas Rosenstein</p>
