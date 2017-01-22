# docbrowser

Docbrowser is a simple Python web application that serves static content, such
as API documentation, and inserts a header that allows to switch between
different versions of the documentation. The design and behaviour of the header
can be implemented for each documentation mount using a custom JavaScript file
and Stylesheet.

### Requirements

- Python
- Flask

To run Docbrowser, use `python run.py` (your choice of Python 2 or 3).

### Configuration

Edit `config.py` to configure Docbrowser. Below is a description of the
available configuration fields.

#### address

The address of the DocBrowser server. The default value is `localhost:8000`.
It is recommended to hide the DocBrowser server behind an NGinx Proxy or serve
using `uwsgi`.

#### debug

Whether to run the DocBrowser Flask app in debug mode. Defaults to `False`.
Can be overwritten using the `--debug` flag when using the `run.py` script.

#### mounts

A list of `docbrowser.Mount()` objects that specify the information for a set
of related documentations. Example:

```python
from docbrowser import Mount

mounts = [
  Mount(
    name = 'Example Documentation',
    slug = 'example',
    path = os.path.join(os.path.dirname(__file__), 'example')
  )
]
```

The `docbrowser.Mount()` constructor takes the following parameters:

- **name**: The name of the documentation. This name will usually be displayed
  in the header above the documentation HTML file.
- **slug**: The name under which the documentation be can be reached in the
  DocBrowser URL format, eg. `/doc/example` when the value for **slug** is
  `'example'`
- **path**: The absolute path to a directory that contains the documentation
  in different versions. The name of the directories must be the version number
  of the documentation.
- **aliases**: A dictionary that maps an alias to a real version number. The
  real version number can also be a callable `fun(versions) -> version`. The
  default value for this parameter is

    ```python
    aliases = {
      'latest': lambda versions: versions[-1]
    }
    ```

  which selects the newest version on the sorted `versions` list.
- **index_files**: A list of filenames that are treated as HTML index files.
  Defaults to `['index.html', 'index.htm']`.
- **index_redirect**: The name of a version or an alias that you will be
  redirected to if you visit the mount URL without a version number. Defaults
  to `'latest'`.
- **version_sort**: A function `fun(v1, v2) -> bool` that returns True if
  *v1* is a smaller version number than *v2*.
- **header_style**: An absolute path to a CSS file that will be returned for
  the `/static/SLUG/style.css` URL. If the `_docbrowser` directory is present
  in the documentation *path*, this parameter defaults to the filename
  `_docbrowser/style.css`, otherwise it will fallback on the DocBrowser default
  style.
- **header_script**: An absolute path to a JavaScript file that will be returned
  for the `/static/SLUG/script.js` URL. If the `_docbrowser` directory is
  present in the documentation *path*, this parameter defaults to the filename
  `_docbrowser/script.js`, otherwise it will fallback on the DocBrowser default
  script.
- **cdn_scripts**: A list of URLs to JavaScript files to include before the
  **header_script**. Defaults to `['https://d3js.org/d3.v4.min.js']`, thus
  making D3.js available by default.

---

<p align="center">Copyright &copy; 2017 &ndash; Niklas Rosenstein</p>
