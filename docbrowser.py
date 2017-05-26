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
import config from './config.json'
import sites from './sites'

app = flask.Flask(__name__)
app.debug = config['debug']
app.config['SERVER_NAME'] = config['server']
app.jinja_env.globals.update({
  'url_for': lambda *a, **k: flask.url_for(*a, **k).rstrip('/'),
  'static': lambda fn: flask.url_for('static', filename=fn)
})

@app.route('/')
def index():
  return flask.render_template(
    'docbrowser/index.html',
    sites=sites.get_sites(with_versions=True)
  )

@app.route('/view/<slug>')
@app.route('/view/<slug>/<version>')
@app.route('/view/<slug>/<version>/<path:file>')
def view(slug, version=None, file=None):
  if version is None:
    # Redirect to the best applicable version (either 'latest' if that
    # alias is defined, or otherwise the highest version).
    try:
      version = sites.get_index_redirect(slug)
      file = sites.get_index_file(slug, version)
    except sites.NotFound:
      flask.abort(404)
    return flask.redirect(
      flask.url_for('view', slug=slug, version=version, file=file)
    )
  if file is None:
    try:
      file = sites.get_index_file(slug, version)
    except sites.NotFound:
      flask.abort(404)
    return flask.redirect(
      flask.url_for('view', slug=slug, version=version, file=file)
    )

  try:
    return sites.serve_static_file(slug, version, file)
  except sites.NotFound:
    flask.abort(404)

@app.errorhandler(404)
def error_404(exc):
  return flask.Response(
    flask.render_template('docbrowser/404.html'),
    404
  )

if require.main == module:
  app.run(host=config['host'], port=config['port'])
