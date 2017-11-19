# docgen

Pythonista markdown document generator from a single file, intended to be used to generate documentation for Github. Included in the generated documentation are:
      
* Module-level docstring.
* Classes and their functions, with
docstrings.
* Module-level functions and their docstrings.
* Decorators are included, with the following special cases:
  * Properties are placed in a separate section, using the docstring of the getter.
  * `on_main_thread` decorators are ignored.
* A table of contents.
      
Functions and methods that start with '_' are not included in the documentation.

# Usage

Include this script in the Pythonista action (wrench) menu, and run it to generate documentation for the file currently open in the editor.

You can choose to just view the resulting documentation as HTML, or also save it as either `README.md` or `<script_name>.md`.

![Menu image](https://raw.githubusercontent.com/mikaelho/docgen/master/menu.png)

Table of contents is included after the module docstring.

There are some special directives you can use to fine-tune the output. These are magic comment strings that must be preceeded only by white space.
  
* `#docgen-toc` - Table of contents will replace this string if found in the module docstring, so that you can have the ToC in the middle of it instead of at the end.
* `#docgen: ` (with a space after the colon) - Use to group functions into related groups. The text you provide after the colon will be included in the table of contents.

# API

* [Class: Processor](#class-processor)
  * [Methods](#methods)
* [Functions](#functions)
  * [Utility functions](#utility-functions)


## Class: Processor

Methods to generate markdown documentation
from source classes, functions and their
docstrings. 

## Methods


#### `get_markdown(self, include_undocumented=False)`

  Produces the markdown for the file.
  
  Optional arguments:
    
  * `include_undocumented` - set to `True` to include classes and methods without a docstring.

#### `get_sections(self)`


#### `get_section_title(self, line_no)`


#### `for_classes(self)`


#### `for_functions(self, c, heading, toc_level)`


#### `build_toc(self, toc)`

# Functions


#### UTILITY FUNCTIONS
#### `el(parent, astdef)`


#### `eldoc(body, astdef)`


#### `slugify(s)`

  Simplifies ugly strings into something URL-friendly.
  
  ```
  slugify("[Some] _ Article's Title--") --> some-articles-title
  ```
  
  From http://blog.dolphm.com/slugify-a-string-in-python/
