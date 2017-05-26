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
      "./preprocessor"
    ]
  }
}
```
"""

import flask
import os
import config from './config.json'
import decorators from './decorators'

class NotFound(Exception):
  pass

def get_site(site_slug):
  """
  Returns a site by its slug.
  """

  for site_name, site in config['sites'].items():
    if site['slug'] == site_slug:
      return site_name, site
  raise NotFound(site_slug)

@decorators.as_list
def get_sites(with_versions=False):
  """
  Returns a list of (name, slug) tuples of all available sites.
  """

  for site_name, site in config['sites'].items():
    result = (site_name, site['slug'])
    if with_versions:
      result += get_versions(site['slug'])
    yield result

def get_versions(site_slug):
  """
  Returns two lists of all the available versions of a site. The first list
  contains all versions found in the site directory, the other list contains
  the aliases.

  Raises #NotFound if the site does not exist.
  """

  site = get_site(site_slug)[1]
  versions = []

  dirname = os.path.expanduser(site['path'])
  if os.path.isdir(dirname):
    for name in os.listdir(dirname):
      if os.path.isdir(os.path.join(dirname, name)):
        versions.append(name)

  versions.sort()
  aliases = list(site.get('aliases', {}).keys())
  return versions, aliases

def get_index_redirect(site_slug):
  """
  Returns the version name to redirect to when accessing a site's index page.

  Raises #NotFound if the site does not exist or when there are no
  versions that we can redirect to.
  """

  site = get_site(site_slug)[1]
  version = site.get('index_redirect')
  if 'latest' in site.get('aliases', {}):
    version = 'latest'
  else:
    versions = get_versions(site_slug)[0]
    if not versions:
      raise NotFound('{}/{}'.format(site_slug))
    version = versions[-1]

  return version

def serve_static_file(site_slug, version, file):
  """
  Returns a file's contents. If the file is an HTML file, it will be
  preprocessed.
  """

  site_name, site = get_site(site_slug)
  aliases = site.get('aliases')
  alias = None
  if aliases and version in aliases:
    alias, version = version, aliases[version]
    if version == '$highest':
      versions = get_versions(site_slug)[0]
      if not versions:
        raise NotFound('{}/{}'.format(site_slug, version))
      version = versions[-1]

  request_file = file
  dirname = os.path.join(site['path'], version)
  if not file:
    for index_file in site.get('index_files', ['index.html', 'index.htm']):
      if os.path.isfile(os.path.join(dirname, index_file)):
        file = index_file
        break
    else:
      raise NotFound('{}/{}'.format(site_slug, version))

  filename = os.path.join(dirname, file)
  if not os.path.isfile(filename):
    raise NotFound('{}/{}/{}'.fomrat(site_slug, version, file))

  if filename.endswith('.html') or filename.endswith('.htm'):
    # Preprocess the contents of the page.
    with open(filename) as fp:
      html = fp.read()
    data = {
      'alias': alias,
      'version': version,
      'file': request_file,
      'site_name': site_name
    }
    for preproc in site.get('preprocessors', ['./preprocessor']):
      html = require(preproc).preprocess_html(
        module.namespace, site, data, html
      )
    return flask.Response(html, mimetype='text/html')

  return flask.send_from_directory(dirname, file)
