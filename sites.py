# Copyright (c) 2017  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the follo  wing conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Handles processing the site configuration. A site is configured like this:

```json
{
  "name": {
    "slug": "slug",
    "path": "path/to/directory/with/different/versions",
    "index_files": ["index.html", "index.htm"],
    "index_redirect: "latest",
    "aliases": {
      "latest": "$highest",
      "stable": "directory-name"
    },
    "preprocessor": [
      "./docbrowser-preprocessor"
    ]
  }
}
```

A pre-processor must provide a `preprocess_html(config, site_config, version, path, html)`
member which must return a modified version of *html*.
"""

import config from './config.json'

class NotFound(Exception):
  pass

def get_versions(site_name):
  """
  Returns two lists of all the available versions of a site. The first list
  contains all versions found in the site directory, the other list contains
  the aliases.

  Raises #NotFound if the site does not exist.
  """

  site = config['sites'].get(site_name)
  if site is None:
    raise NotFound(site_name)
  versions = []

  dirname = os.path.expanduser(site['path'])
  if os.path.isdir(dirname):
    for name in os.listdir(dirname):
      if os.path.isdir(os.path.join(dirname, name)):
        versions.append(name)

  versions.sort()
  aliases = list(site.get('aliases', {}).keys())
  return versions, aliases

def get_index_redirect(site_name):
  """
  Returns the version name to redirect to when accessing a site's index page.

  Raises #NotFound if the site does not exist or when there are no
  versions that we can redirect to.
  """

  site = config['site'].get(site_name)
  if site is None:
    raise NotFound(site_name)

  version = site.get('index_redirect')
  if 'latest' in site.get('aliases', {}):
    version = 'latest'
  else:
    versions = get_versions(site_name)[0]
    if not versions:
      raise NotFound('{}/{}'.format(site_name))
    version = versions[-1]

  return version

def get_file_contents(site_name, version, file):
  """
  Returns a file's contents. If the file is an HTML file, it will be
  preprocessed.
  """

  site = config['site'].get(site_name)
  if site is None:
    raise NotFound(site_name)

  aliases = site.get('aliases')
  if aliases and version in aliases:
    version = aliases[version]
    if version == '$highest':
      versions = get_versions(site_name)
      if not versions:
        raise NotFound('{}/{}'.format(site_name, version))
      version = versions[-1]

  filename = os.path.join(site['path'], version, file)
  if not os.path.isfile(filename):
    raise NotFound('{}/{}/{}'.format(site_name, version, file)

  return filename
