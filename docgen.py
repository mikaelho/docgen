# coding: utf-8

"""Pythonista markdown document generator from single file docstrings

Intended to be used to generate documentation for Github. Included in the
generated documentation are:

* Module-level docstring.
* Classes and their functions, with docstrings.
* Module-level functions and their docstrings.
* Decorators are included, with the following special cases:
  * Properties are placed in a separate section, using the docstring of the
    getter.
  * `on_main_thread` decorators are ignored.
* A table of contents.

Functions and methods that start with '_' are not included in the
documentation.

# Usage

Include this script in the Pythonista action (wrench) menu, and run it to
generate documentation for the file currently open in the editor.

You can choose to just view the resulting documentation as HTML, or also
save it as either `README.md` or `<script_name>.md`.

![Menu image](https://raw.githubusercontent.com/mikaelho/docgen/master/menu.png)

Table of contents is included after the module docstring.

There are some special directives you can use to fine-tune the output. These
are magic comment strings that must be preceeded only by white space.

* `#docgen-toc` - Table of contents will replace this string if found in the
  module docstring, so that you can have the ToC in the middle of it instead
  of at the end.
* `#docgen: ` (with a space after the colon) - Use to group functions into
  related groups. The text you provide after the colon will be included in
  the table of contents.
"""

__version__ = '1.0'

import editor, console, ui, markdown2
import ast, os, re


class Processor():
    """ Methods to generate markdown documentation from source classes,
    functions and their docstrings. """

    def __init__(self):
        ''' Initialize document generator from the
        Python file open in the editor. '''
        file_text = editor.get_text()
        self.tree = ast.parse(file_text)
        self.lines = file_text.splitlines()
        self.section_lines = []
        self.section_titles = {}
        self.used_section_titles = set()


    def get_markdown(self, include_undocumented=False):
        """ Produces the markdown for the file.

        Optional arguments:

        * `include_undocumented` - set to `True` to include classes and methods
          without a docstring.
        """

        result = ''

        default_start = ('# ' + os.path.basename(editor.get_path())[:-3] +
                         '\n\n')
        module_doc = ast.get_docstring(self.tree) or ''
        if not module_doc.strip().startswith('# '):
            result += default_start
        result += module_doc + '\n\n'

        self.get_sections()

        toc = []

        classes_result, classes_toc = self.for_classes()
        toc += classes_toc

        func_result, func_toc = self.for_functions(self.tree, 'Functions', 0)
        toc += func_toc

        api_result = ''
        if len(toc) > 0:
            api_result += '# API\n\n'
            api_result += self.build_toc(toc) + '\n\n'
        api_result += classes_result + func_result

        toc_magic = '#docgen-toc'
        if result.strip().find(toc_magic) == 0:
            return result.replace(toc_magic, api_result)
        else:
            return result + api_result


    def get_sections(self):
        magic_string = '#docgen: '
        for line_no, line in enumerate(self.lines):
            if line.strip().find(magic_string) == 0:
                self.section_lines.append(line_no + 1)
                self.section_titles[line_no + 1] = \
                    line.strip()[len(magic_string):]


    def get_section_title(self, line_no):
        for section_line_no in self.section_lines:
            if section_line_no >= line_no:
                break
            if (line_no - section_line_no < 5 and
                    section_line_no not in self.used_section_titles):
                title = self.section_titles[section_line_no]
                self.used_section_titles.add(section_line_no)
                return title
        return None


    def for_classes(self):
        classes = list(el(self.tree, ast.ClassDef))
        toc = []
        result = ''

        for c in classes:
            heading = 'Class: ' + c.name
            result += '## ' + heading + '\n\n'
            toc.append((heading, 0))
            docstr = ast.get_docstring(c)
            if docstr:
                result += docstr + '\n\n'

            func_result, func_toc = self.for_functions(c, 'Methods', 1)

            result += func_result
            toc += func_toc

        return result, toc


    def for_functions(self, c, heading, toc_level):
        funcs = list(el(c, ast.FunctionDef))
        property_operations = {}
        property_docstrings = {}
        result = ''
        toc = []

        if len(funcs) > 1:
            func_heading = "#" * (toc_level + 1) + ' ' + heading + '\n\n'
            result += func_heading
            toc.append((heading, toc_level))

        for f in funcs:
            section_title = self.get_section_title(f.lineno)
            if section_title:
                result += '\n#### ' + section_title.upper()
                toc.append((section_title, toc_level + 1))

            if f.name.startswith('_'): continue
            line_actual = f.lineno
            descriptors = []
            property_descriptor = False
            while True:
                stripped = self.lines[line_actual - 1].strip()
                if stripped.startswith('@'):
                    line_actual += 1
                    if stripped == '@on_main_thread':
                        continue
                    if stripped == '@property':
                        property_operations[f.name] = ['get']
                        docstr = ast.get_docstring(f)
                        if docstr:
                            property_docstrings[f.name] = docstr
                        property_descriptor = True
                    elif stripped.endswith('.setter'):
                        property_operations[f.name].append('set')
                        property_descriptor = True
                    elif stripped.endswith('.deleter'):
                        property_operations[f.name].append('del')
                        property_descriptor = True
                    descriptors.append(stripped)
                else:
                    break
            if property_descriptor:
                continue
            descriptor_str = '`' + ', '.join(descriptors) + '`\n' if len(
                descriptors) > 0 else ''
            while not stripped.endswith(':'):
                line_actual += 1
                stripped += self.lines[line_actual - 1].strip()
            result += ('\n#### `' + stripped[len('def '):-1] + '`\n' +
                       descriptor_str + '\n')
            docstr = ast.get_docstring(f)
            if docstr:
                for line in iter(docstr.splitlines()):
                    result += '  ' + line + '\n'

        if len(property_operations) > 0:
            prop_heading = "#" * (toc_level + 1) + ' Properties\n\n'
            result += prop_heading
            toc.append(('Properties', toc_level))
            for prop in property_operations:
                result += '\n#### `' + prop + ' (' + ', '.join(
                    property_operations[prop]) + ')`\n\n'
                docstr = property_docstrings.get(prop, None)
                if docstr:
                    for line in iter(docstr.splitlines()):
                        result += '  ' + line + '\n'

        return result, toc


    def build_toc(self, toc):
        result = ''
        for title, level in toc:
            result += '  ' * level
            result += '* [' + title + '](#' + slugify(title) + ')\n'
        return result


# docgen: Utility functions

def el(
        parent,
        astdef):
    return (e for e in parent.body if isinstance(e, astdef))


def eldoc(body, astdef):
    mds = el(body, astdef)
    md_list = list(mds)
    return_value = ''
    for md in mds:
        return_value += md + '\n\n'
    return return_value


def slugify(s):
    """
    Simplifies ugly strings into something URL-friendly.

    ```
    slugify("[Some] _ Article's Title--") --> some-articles-title
    ```

    From http://blog.dolphm.com/slugify-a-string-in-python/
    """

    # "[Some] _ Article's Title--"
    # "[some] _ article's title--"
    s = s.lower()

    # "[some] _ article's_title--"
    # "[some]___article's_title__"
    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')

    # "[some]___article's_title__"
    # "some___articles_title__"
    s = re.sub('\W', '', s)

    # "some___articles_title__"
    # "some   articles title  "
    s = s.replace('_', ' ')

    # "some   articles title  "
    # "some articles title "
    s = re.sub('\s+', ' ', s)

    # "some articles title "
    # "some articles title"
    s = s.strip()

    # "some articles title"
    # "some-articles-title"
    s = s.replace(' ', '-')

    return s


if __name__ == '__main__':

    filename = os.path.basename(editor.get_path())[:-3]

    choice = console.alert('docgen',
        'Create markdown document out of docstrings', 'View as HTML',
        'Also save as README.md', 'Also save as ' + filename + '.md')

    result = Processor().get_markdown()

    # print(result)

    v = ui.WebView()
    v.present()
    v.load_html(markdown2.markdown(result))

    if choice > 1:
        md_dirname = os.path.dirname(editor.get_path())
        md_filename = 'README.md' if choice == 2 else filename + '.md'

        with open(md_dirname + '/' + md_filename, 'w', encoding='utf-8') as f:
            f.write(result)
