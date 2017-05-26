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
The default docbrowser preprocessor.
"""

import flask
import textwrap

def preprocess_html(sites, site, data, html):
  versions, aliases = sites.get_versions(site['slug'])
  content = flask.render_template(
    'docbrowser/partials/inject.html',
    name=data['site_name'], file=data['file'],
    current_alias=data['alias'], current_version=data['version'],
    aliases=aliases, versions=versions, slug=site['slug'],
    disqus_id=sites.config.get('disqus_id'),
    disqus_page_url=flask.url_for(
      'view', slug=site['slug'], version=data['version'], file=data['file'], _external=True
    ),
    disqus_page_identifier=flask.request.path
  )

  # Insert the content right at the end of the <body> tag.
  index = html.find('</body>')
  if index >= 0:
    html = html[:index] + content + html[index:]

  return html
