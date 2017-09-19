# docgen

Pythonista markdown document generator from a single file, intended to be used to generate documentation for Github. What's included:
      
* Module-level docstring.
* Classes and their functions, with
docstrings.
* Module-level functions and their docstrings.
      
Functions and methods that start with '_' are not included in the documentation.

# Usage

To be included.

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


#### ` get_markdown(self, include_undocumented=False)`

  Produces the markdown for the file.
  
  Optional arguments:
    
    * `include_undocumented` - set to `True` if
    you do not want to skip classes and methods without a docstring.

#### ` get_sections(self)`


#### ` get_section_title(self, line_no)`


#### ` for_classes(self)`


#### ` for_functions(self, c, heading, toc_level)`


#### ` build_toc(self, toc)`

# Functions


#### UTILITY FUNCTIONS
#### ` el(parent, astdef)`


#### ` eldoc(body, astdef)`


#### ` slugify(s)`

  Simplifies ugly strings into something URL-friendly.
  
  >>> print slugify("[Some] _ Article's Title--")
  some-articles-title
  
  From http://blog.dolphm.com/slugify-a-string-in-python/
