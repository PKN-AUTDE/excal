
# Table of Contents

1.  [ECAL - Extendable Clang AST based Linter.](#org02fa096)
    1.  [Plugins](#orgad34be7)


<a id="org02fa096"></a>

# ECAL - Extendable Clang AST based Linter.

This is a simple project implementing a C/C++ linter based on the clang AST. The main porpoise is to create a tool which is easily extendable via plugins.


<a id="orgad34be7"></a>

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

Additionally the plugin needs to be registered in the plugins.json file.

```
    {
      "plugins": ["plugins.myPlugin"]
    }
```

All possible functions can be seen in src/visitor.py. To see which function may be needed for your use-cases run the ecal project using the -p flag. This will print an AST of the desired file.

