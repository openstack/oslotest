# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'openstackdocstheme',
    'reno.sphinxext',
]

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'oslotest Release Notes'
copyright = '2016, oslotest Developers'

# Release notes do not need a version in the title, they span
# multiple versions.
# The full version, including alpha/beta/rc tags.
release = ''
# The short X.Y version.
version = ''

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'openstackdocs'

# -- openstackdocstheme configuration -------------------------------------

openstackdocs_repo_name = 'openstack/oslotest'
openstackdocs_bug_project = 'oslotest'
openstackdocs_bug_tag = ''
openstackdocs_auto_name = False
