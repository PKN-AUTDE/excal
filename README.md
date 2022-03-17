# EXCAL - Extendable Clang AST based Linter.

This is a simple project implementing a C/C++ linter based on the clang AST. The main porpoise is to create a tool which is easily extendable via plugins.

The focus of this project is to provide a tool for the implementation of custom C/C++ coding guidelines. There are no rules provided by the linter itself, rather a toolset to implement your own. (see Plugins)

## Installation

In order to use excal you need to have [clang](http://clang.org/) installed on your system.

This tool is available on PyPI so you can install it via pip:

```
pip install excal

```

## Usage

To Analyze a file or project the tool expects input files/directories. Additionally you should provide all includes. If no Includes are given Clang will still create an AST, however it will be incomplete and may cause false positives/negatives from the linter.


```
    excal -f path/to/file_to_analyze.c -i path/to/includes/
```


A list of all supported options: 

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Command</th>
<th scope="col" class="org-left">arguments</th>
<th scope="col" class="org-left">Description</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">-a</td>
<td class="org-left">List of compiler arguments</td>
<td class="org-left">provide compiler arguments for Clang, may improve the AST</td>
</tr>


<tr>
<td class="org-left">&#x2013;argfile</td>
<td class="org-left">File</td>
<td class="org-left">Compiler arguments may be provided in a File, seperated by newlines</td>
</tr>


<tr>
<td class="org-left">-i</td>
<td class="org-left">List of files/directories</td>
<td class="org-left">Include Files used by the compiler to build the AST</td>
</tr>


<tr>
<td class="org-left">-f (required)</td>
<td class="org-left">List of files/directories</td>
<td class="org-left">Files/Directories to analyze.</td>
</tr>


<tr>
<td class="org-left">-e</td>
<td class="org-left">List of files/directories</td>
<td class="org-left">Files/Directories within given directories, which should be ignored.</td>
</tr>


<tr>
<td class="org-left">-p</td>
<td class="org-left">-</td>
<td class="org-left">If this flag is provided the Linter will print the AST of all included files. This is useful for creating Plugins.</td>
</tr>


<tr>
<td class="org-left">-ptt</td>
<td class="org-left">-</td>
<td class="org-left">Same as above, but will also Print all Tokens under their corresponding AST Nodes. (will produce long output)</td>
</tr>

<tr>
<td class="org-left">-cpp</td>
<td class="org-left">-</td>
<td class="org-left">Libclang will analyze files based on their extension. If the extension is not cpp specific (eg. .h instead .hpp) this flag will force all files to be analyzed as c++ code.</td>
</tr>


<tr>
<td class="org-left">-ext</td>
<td class="org-left">List of file extensions</td>
<td class="org-left">If provided only files with the given extensions will be parsed.</td>
</tr>
</tbody>
</table>


### Config files
If a single directory is given as input, excal will scan its root for a setup.cfg file. Here some project parameters may be provided. At the moment only the options given in belows example are being used, additional ones will be added.

```
[EXCAL]
includes = 
  /opt/ros/foxy/include/
exclude_files =
  file/to/exclude.c
  files/to/exclude/
  **/venv
force_cpp = True
```


## Plugins

The Goal of this project is to provide an interface that allows it to easily implement linter rules based on an AST.

A Plugin will need to provide a register method in which it will register itself within the Project. The Plugin then can provide a class inherits from the NodeVisitor class. Here the visit_X functions can be overwritten. When parsing the AST, these functions will be called whenever a desired Node is reached. From there further operations may be done on the provided AstNode.

See the following example:
```
    from visitor import NodeVisitor
    from pluginManager import PluginManager
    from astNode import AstNode
    
    PLUGIN_NAME = "AutonomusReply"
    
    class customVisitor(NodeVisitor):
        def __init__(self) -> None:
            super().__init__()
    
        def visit_class_base(self, node: AstNode) -> None:
            return
    
    def register(pm: PluginManager):
        pm.register(PLUGIN_NAME, customVisitor)
```


There are two ways to provide Plugins. The preferred one is to Create as a standalone python Package. [See this example](https://github.com/PKN-AUTDE/excal-example-plugin).

The other way is to put the Plugin in the plugins folder and register it in the plugins.json file.

```
    {
      "plugins": ["plugins.myPlugin"]
    }
```

All possible functions can be seen in src/visitor.py. To see which function may be needed for your use-cases run the excal project using the -p flag. This will print an AST of the desired file.

