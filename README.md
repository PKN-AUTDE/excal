# EXCAL - Extendable Clang AST based Linter.

This is a simple project implementing a C/C++ linter based on the clang AST. The main porpoise is to create a tool which is easily extendable via plugins.



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


There are two ways to provide Plugins. The preferred one is to Create as a standalone python Package, an example will be linked here soon.
The other way is to put the Plugin in the plugins folder and register it in the plugins.json file.

```
    {
      "plugins": ["plugins.myPlugin"]
    }
```

All possible functions can be seen in src/visitor.py. To see which function may be needed for your use-cases run the excal project using the -p flag. This will print an AST of the desired file.

