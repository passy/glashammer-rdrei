import os, _ast, linecache, imp

from werkzeug import run_simple

def run_very_simple(app):
    from werkzeug.debug import DebuggedApplication
    app = DebuggedApplication(app, True)
    run_simple('localhost', 6060, app, use_reloader=True)

# system utilities

can_build_eventmap = True
def build_eventmap(app):
    """Walk through all the builtins and plugins for an application and
    look for `emit_event` calls. This is useful for plugin developers that
    want to find possible entry points without having to dig the source or
    missing documentation. Speaking of documentation: This could help for
    that too.
    """
    if not can_build_eventmap:
        raise RuntimeError('this feature requires python 2.5')
    import glashammer

    textpress_root = os.path.realpath(os.path.dirname(glashammer.__file__))
    searchpath = [(textpress_root, '__builtin__')]

    #for plugin in app.plugins.itervalues():
    #    path = os.path.realpath(plugin.path)
    #    if os.path.commonprefix([textpress_root, path]) != textpress_root:
    #        searchpath.append((plugin.path, plugin.name))

    def walk_ast(ast):
        if isinstance(ast, _ast.Call) and \
           isinstance(ast.func, _ast.Name) and \
           ast.func.id in ('emit_event', 'iter_listeners') and \
           ast.args and \
           isinstance(ast.args[0], _ast.Str):
            yield ast.args[0].s, ast.func.lineno
        for field in ast._fields or ():
            value = getattr(ast, field)
            if isinstance(value, (tuple, list)):
                for node in value:
                    if isinstance(node, _ast.AST):
                        for item in walk_ast(node):
                            yield item
            elif isinstance(value, _ast.AST):
                for item in walk_ast(value):
                    yield item

    def find_help(filename, lineno):
        help_lines = []
        lineno -= 1
        while lineno > 0:
            line = linecache.getline(filename, lineno).strip()
            if line.startswith('#!'):
                line = line[2:]
                if line and line[0] == ' ':
                    line = line[1:]
                help_lines.append(line)
            elif line:
                break
            lineno -= 1
        return '\n'.join(reversed(help_lines)).decode('utf-8')

    result = {}
    for folder, prefix in searchpath:
        offset = len(folder)
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                filename = os.path.join(dirpath, filename)
                shortname = filename[offset:]
                data = ''.join(linecache.getlines(filename))
                ast = compile(''.join(linecache.getlines(filename)),
                              filename, 'exec', 0x400)

                for event, lineno in walk_ast(ast):
                    help = find_help(filename, lineno)
                    result.setdefault(event, []).append((prefix, shortname,
                                                         lineno, help))

    return result


def load_app_from_path(modulepath, factory_name='create_app'):
    """
    Load the module containg the application and create it.
    """

    modulepath = os.path.abspath(modulepath)
    filename = os.path.basename(modulepath)
    modulename = os.path.splitext(filename)[0]
    dirpath = os.path.dirname(modulepath)

    mfile, mpath, mdesc = imp.find_module(modulename, [dirpath])

    mod = imp.load_module('gh_runner', mfile, mpath, mdesc)

    mfile.close()

    factory = getattr(mod, factory_name, None)
    if factory is None:
        raise AttributeError('Application factory %s not found' %
                             factory_name)
    app = factory()
    return app

