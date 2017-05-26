/* Copyright (c) 2017  Niklas Rosenstein
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the follo  wing conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 *
 * This is the DocBrowser default script which inserts a header into the page. */

(function () {
  var createVersionSelector = function () {
    /* Create an HTML node which allows you to select the version. The node
     * will float on the bottom-left side of the HTML page. */
    var ci = docbrowser_versions.findIndex(function (x) { return x == docbrowser_currentversion })
    var root = d3.select("body").append('div').classed('docbrowser docbrowser-root', true)
    var selection = root.selectAll('div')
      .data(docbrowser_versions)
      .enter().append('div')
      .each(function (d, i) {
        if (i == ci)
          d3.select(this).classed('docbrowser-version-current', true)
      })

    var hide = function (d, i) {
      if (i != ci) {
        d3.select(this).style('display', 'none')
      }
    }
    selection.each(hide)

    selection
      .classed('docbrowser docbrowser-version', true)
      .text(function (d) { return d; })
      .on("mouseover", function () {
        var count = selection.size() - 1;
        selection.transition().style('left', function (d, i) { return 5 + 55 * i + 'px'; })
          .on("start", function (d, i) { selection.style('display', 'block') })
      })
      .on("mouseleave", function () {
        selection.transition().delay(100).style('left', '15px').on("end", hide);
      })
      .on('click', function(d, i) {
        document.location = docbrowser_urls[i]
      })
  }
  window.addEventListener('load', createVersionSelector, false)
})()
