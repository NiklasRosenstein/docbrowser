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

import bs4
import flask
import os
import sys

app = flask.Flask(__name__)

import config


def preprocess_configuration():
  for mount in config.mounts:
    mount.setdefault('slug', mount['name'])
    mount.setdefault('aliases', {})
    mount.setdefault('index_file', 'index.html')
    mount.setdefault('version_sort', lambda v1, v2: v1 < v2)

def find_mount_by_slug(slug):
  " Finds information on a mount by the given *slug* or aborts with 404. "
  for mount in config.mounts:
    if mount['slug'] == slug:
      return mount
  flask.abort(404)

def get_mount_versions(mount):
  if os.path.isdir(mount['path']):
    versions = []
    for item in os.listdir(mount['path']):
      if os.path.isdir(os.path.join(mount['path'], item)):
        versions.append(item)
    versions.sort(cmp=mount['version_sort'])
    return list(mount.get('aliases', {}).keys()) + versions
  return []

def serve_doc_file(mount, version, file, undoc=False):
  real_version = mount['aliases'].get(version, version)
  if callable(real_version):
    real_version = real_version(get_mount_versions(mount))
  path = os.path.join(mount['path'], real_version, file)
  if not os.path.exists(path):
    flask.abort(404)
  if os.path.isdir(path):
    path = os.path.join(path, mount['index_file'])

  if not undoc and (path.endswith('.htm') or path.endswith('.html')):
    with open(path) as fp:
      soup = bs4.BeautifulSoup(fp.read(), config.html_parser)
    wrapper = soup.new_tag('div', **{'data-role': 'content'})
    body_children = list(soup.body.children)

    # Render the header content and append it to the HTML page.
    header_string = flask.render_template(
      'docbrowser/header.jhtml', current_version=version, mount=mount,
      current_real_version=real_version, versions=get_mount_versions(mount)
    )
    header_soup = bs4.BeautifulSoup(header_string, config.html_parser)

    if soup.head and header_soup.head:
      for child in list(header_soup.head.children):
        soup.head.append(child)
    elif header_soup.head:
      soup.body.insert_before(header_soup.head)

    soup.body.append(header_soup.div)
    soup.body.append(wrapper)
    for child in body_children:
      wrapper.append(child)
    return soup.prettify(formatter=config.html_formatter)

  dirname, filename = os.path.split(path)
  return flask.helpers.send_from_directory(dirname, filename)

@app.route('/')
def index():
  docs = []
  for mount in config.mounts:
    versions = get_mount_versions(mount)
    docs.append({'info': mount, 'versions': versions})
  return flask.render_template('docbrowser/index.jhtml', docs=docs)

@app.route('/doc/<slug>')
def doc_index(slug):
  mount = find_mount_by_slug(slug)
  return flask.redirect(flask.url_for(
    'doc', slug=slug, version=mount['index_redirect']
  ))

def doc(slug, version, file=''):
  mount = find_mount_by_slug(slug)
  return serve_doc_file(mount, version, file)

app.add_url_rule('/doc/<slug>/<version>/', 'doc', doc)
app.add_url_rule('/doc/<slug>/<version>/<path:file>', 'doc', doc)

preprocess_configuration()
