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
A Python web application serving static content, such as API documentation,
that inserts a little header to switch between different versions of the
content.
"""

import flask
import os
import sys
import textwrap
import werkzeug

app = flask.Flask(__name__, static_folder=None)

class Mount(object):
  """
  Represents information on a set of documentations.
  """

  def __init__(self, name, slug, path, aliases=None, index_files=None,
               index_redirect='latest', version_sort=None, header_style=None,
               header_script=None, cdn_scripts=None):
    if aliases is None:
      aliases = {'latest': lambda versions: versions[-1]}
    if index_files is None:
      index_files = ['index.html', 'index.html']
    if version_sort is None:
      version_sort = lambda v1, v2: v1.lower() > v2.lower()
    if cdn_scripts is None:
      cdn_scripts = ['https://d3js.org/d3.v4.js']

    self.name = name
    self.slug = slug
    self.path = path
    self.aliases = aliases
    self.index_files = index_files
    self.index_redirect = index_redirect
    self.version_sort = version_sort
    self.header_style = header_style
    self.header_script = header_script
    self.cdn_scripts = cdn_scripts

  def get_header_style(self):
    if self.header_style:
      return self.header_style
    filename = os.path.join(self.path, '_docbrowser/style.css')
    if os.path.isfile(filename):
      return filename
    return None

  def get_header_script(self):
    if self.header_script:
      return self.header_script
    filename = os.path.join(self.path, '_docbrowser/script.js')
    if os.path.isfile(filename):
      return filename
    return None

  def get_header_style_url(self):
    slug = self.slug if self.get_header_style() else 'docbrowser'
    return '/static/{}/style.css'.format(slug)

  def get_header_script_url(self):
    slug = self.slug if self.get_header_style() else 'docbrowser'
    return '/static/{}/script.js'.format(slug)

  def get_versions(self, aliases=True):
    """
    Lists the available versions and returns it sorted. All defined aliases
    will be prepended unless *aliases* is False.
    """

    versions = []
    if os.path.isdir(self.path):
      for item in os.listdir(self.path):
        if os.path.isdir(os.path.join(self.path, item)):
          versions.append(item)
      versions.sort(cmp=self.version_sort)
      if aliases:
        versions = sorted(self.aliases.keys()) + versions
    return versions

import config


def find_mount_by_slug(slug):
  " Finds information on a mount by the given *slug* or aborts with 404. "
  for mount in config.mounts:
    if mount.slug == slug:
      return mount
  flask.abort(404)

def serve_doc_file(mount, version, file):
  versions = mount.get_versions()
  real_version = mount.aliases.get(version, version)
  if callable(real_version):
    real_version = real_version(versions)
  path = os.path.join(mount.path, real_version, file)
  if os.path.isdir(path):
    # Find a matching index file.
    for item in mount.index_files:
      new_path = os.path.join(path, item)
      if os.path.isfile(new_path):
        path = new_path
        break
    else:
      flask.abort(404)

  if not os.path.isfile(path):
    content = flask.render_template('docbrowser/404.html', path=file)
    status = 404
  elif path.endswith('.htm') or path.endswith('.html'):
    with open(path) as fp:
      content = fp.read()
    status = 200
  else:
    # Send the plain file without preprocessing.
    dirname, filename = os.path.split(path)
    return flask.helpers.send_from_directory(dirname, filename)

  # This is the content that we need to insert into the header.
  urls = [flask.url_for('doc', slug=mount.slug, version=v, file=file)
          for v in versions]
  icontent = textwrap.dedent("""
    <script type="text/javascript">
      var docbrowser_currentversion = "{current_version}"
      var docbrowser_urls = [{urls}]
      var docbrowser_versions = [{versions}]
    </script>
    {cdn_scripts}
    <script src="{header_script}"></script>
    <link rel="stylesheet" href="{header_style}"/>""")\
    .format(
      current_version = version, current_version_real = real_version,
      versions = ','.join('"{}"'.format(x) for x in mount.get_versions()),
      urls = ','.join('"{}"'.format(x) for x in urls),
      header_style = mount.get_header_style_url(),
      header_script = mount.get_header_script_url(),
      cdn_scripts = '\n'.join('<script src="{}"></script>'.format(x) for x in mount.cdn_scripts)
    )

  def generate():
    parsed_header = False
    for line in content.splitlines():
      if not parsed_header:
        index = line.find('</head>')
        if index >= 0:
          line = line[:index] + icontent + line[index:]
          parsed_header = True
        index = line.find('<body>')
        if not parsed_header and index >= 0:
          line = line[:index] + '<head>' + icontent + '</head>' + line[index:]
          parsed_header = True
      yield line

  return flask.Response(generate(), mimetype='text/html')


@app.route('/')
def index():
  return flask.render_template('docbrowser/index.html', docs=config.mounts)

@app.route('/doc/<slug>')
def doc_index(slug):
  mount = find_mount_by_slug(slug)
  return flask.redirect(flask.url_for(
    'doc', slug=slug, version=mount.index_redirect))

def doc(slug, version, file=''):
  mount = find_mount_by_slug(slug)
  return serve_doc_file(mount, version, file)

app.add_url_rule('/doc/<slug>/<version>/', 'doc', doc)
app.add_url_rule('/doc/<slug>/<version>/<path:file>', 'doc', doc)

def serve_mount_static(slug, file):
  mount = find_mount_by_slug(slug)
  if file == 'style.css':
    filename = mount.get_header_style()
  elif file == 'script.js':
    filename = mount.get_header_script()
  else:
    flask.abort(404)
  dirname, filename = os.path.split(filename)
  return flask.helpers.send_from_directory(dirname, filename)

@app.route('/static/<path:filename>')
def static(filename):
  if filename.count('/') == 1:
    slug, file = filename.split('/')
    try:
      return serve_mount_static(slug, file)
    except werkzeug.exceptions.NotFound:
      pass  # Handle normal static file later

  filename = os.path.join(os.path.dirname(__file__), 'static', filename)
  dirname, filename = os.path.split(filename)
  return flask.helpers.send_from_directory(dirname, filename)
