# docbrowser

Docbrowser is a simple Python web application that serves static content, such
as API documentation, and inserts a header that allows to switch between
different versions of the documentation.

__Requirements__

- Python
- Flask
- BeautifulSoup4
- LXML (optional)

To run Docbrowser, use `python run.py` (your choice of Python 2 or 3).

__Configuration__

Edit `config.py` to configure Docbrowser. The default configuration is included
below for reference.

```python
# Configuration file for docbrowser.py

import os

address = 'localhost:8000'
debug = False

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
```

---

<p align="center">Copyright &copy; 2017 &ndash; Niklas Rosenstein</p>
