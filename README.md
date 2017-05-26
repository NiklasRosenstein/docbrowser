# docbrowser

Docbrowser is a simple Python web application that serves static content, such
as API documentation, and inserts a header that allows to switch between
different versions of the documentation. The design and behaviour of the header
can be implemented for each documentation mount using a custom JavaScript file
and Stylesheet.

### Deployment Instructions

  [Node.py]: https://nodepy.org

- Install [Node.py][] in Python 3.3 or newer
- Run `nppm install` to install dependencies
- Run `nodepy .` to run the Docbrowser server

### Configuration

Edit `config.json` to configure Docbrowser.

---

<p align="center">Copyright &copy; 2017 &ndash; Niklas Rosenstein</p>

__Attributions__

- Copyright &copy; Ivan Boyko (under Creative Commons (Attribution 3.0 Unported))
  for the following files: `static/docbrowser/next.png` and
  `static/docbrowser/previous.png` (link: https://www.iconfinder.com/iconsets/arrows-android-l-lollipop)
