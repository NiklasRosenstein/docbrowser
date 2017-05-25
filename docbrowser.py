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
A Node.py-Flask web application that serves static content, such as API
documentation, and inserts a little header to switch between different
versions of the content.
"""

import flask
import os
import sys
import textwrap
import werkzeug
import sites from './sites'

app = flask.Flask(__name__, static_folder=None)



import config


def find_mount_by_slug(slug):
  " Finds information on a mount by the given *slug* or aborts with 404. "
  for mount in config.mounts:
    if mount.slug == slug:
      return mount
  flask.abort(404)

def serve_doc_file(mount, version, file, check_only=False):
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
    flask.abort(404)
  elif path.endswith('.htm') or path.endswith('.html'):
    with open(path) as fp:
      content = fp.read()
    status = 200
  elif not check_only:
    # Send the plain file without preprocessing.
    dirname, filename = os.path.split(path)
    return flask.helpers.send_from_directory(dirname, filename)
  if check_only:
    return None

  # This is the content that we need to insert into the header.
  urls = [flask.url_for('doc', slug=mount.slug, version=v, file=file) + '?doredirect=true'
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
  doredirect = (flask.request.args.get('doredirect') == 'true')
  try:
    mount = find_mount_by_slug(slug)
    response = serve_doc_file(mount, version, file, check_only=doredirect)
  except werkzeug.exceptions.NotFound:
    if doredirect and file:
      return flask.redirect(flask.url_for('doc_index', slug=slug))
    raise
  if doredirect:
    # Redirect to the same page without the ?doredirect=true part.
    return flask.redirect(flask.url_for('doc', slug=slug, version=version, file=file))
  return response

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
