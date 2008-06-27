"""
    simpleconfig
    ~~~~~~~~~~~~

    A parser for simple structured configfiles


    :copyright: 2008 by Ronny Pfannschmidt
    :license: BSD

    Usage:

    >>> config = '''
    ... name = Stuff
    ... 
    ... [Section 1]
    ... path = ./run.sh
    ... '''
    >>> SimpleConfig(config)
    {'name': 'Stuff', 'Section 1': {'path': './run.sh'}}

    >>> project = '''
    ... name = Pida %(dirbase)
    ... 
    ... [controller: Test]
    ... type = unittest
    ... tool = nose
    ... '''
    >>> SimpleConfig(project)
    {('controller', 'Test'): {'tool': 'nose', 'type': 'unittest'}, 'name': 'Pida %(dirbase)'}


    """
__all__ = 'SimpleConfig', 'readmany', 'dumps', 'merge'

from copy import deepcopy


class SimpleConfig(dict):
    """parses ini style line lists

    :param source:
        the data source

        * a file or filename
        * a string containing `\\n`
        * any other iterable over a set of lines
        * a nested dict containing the data
    :param defaults:
        default values for output minimizing output
    """

    
    file = None
    inherit = None
    
    def __init__(self, source=()):
        if isinstance(source, basestring):
            if '\n' in source:
                source = source.splitlines()
            else:
                f = open(source)
                try:
                    source = f.readlines()
                finally:
                    f.close()
        if isinstance(source, dict):
            self.merge(source)
        else:
            self._read_from_lines(source)

    def __str__(self):
        """
        >>> print SimpleConfig({'name': 'hans', ('Command', 'Run'): {'exe': 'bash'}})
        name = hans
        <BLANKLINE>
        [Command: Run]
        exe = bash
        <BLANKLINE>
        """
        result = []
        _dump_w(self, result.extend)
        return ''.join(result)


    def make_section(self, name, line):
        return {}

    def sections(self):
        for k, v in dict.items(self):
            if isinstance(v, dict):
                yield k, v

    def inherit(self, name):
        """may be used for inheriting from other config files"""
        raise NotImplementedError('%s.inherit'%type(self).__name__)

    def _read_from_lines(self, lines):
        result = {}
        # as long as there is no explicit section
        # take the global space as section
        section = result
        for line, name, value in _prepare_lines(lines):
            if not result and name == '#inherit':
                self.inherit(value)
                continue

            if value is None:
                if name in result:
                    raise KeyError('Section %r already exists as %r, line=%d'%(
                                name, result[name],  line
                            ))
                result[name] = section = self.make_section(name, line)
            else:
                if name in section:
                    raise KeyError('Value %r already exists as %r, line=%d'%(
                                name, section[name], line
                            ))
                section[name] = value
        self.merge(result)


    def merge(self, new):
        """merges the content of another config/dict to this config

        :param new: new informations to add
        """
        if not isinstance(new, dict):
            new = type(self)(new)

        for k, v in new.items():
            if isinstance(self.get(k), dict):
                if isinstance(v, dict):
                    self[k].update(v)
                else:
                    raise ValueError('%r cant update the dict at %r'%(v, k))
            else:
                self[k] = v

    def dump_file(self, path):
        f = open(path, 'w')
        f.write(str(self))
        f.close()


def readmany(*sources):
    """reads from many sources at once, merges into a single result"""
    merged = SimpleConfig()
    for source in sources:
        merged.merge(source)
    return merged


class simple_section(dict):
    """Helper class for keeping the sections in 
    `OrderedSectionsConfig` sorted by the line
    """
    __slots__ = 'name', 'line'
    def __init__(self, name, line):
        dict.__init__(self)
        self.name = name
        self.line = line


class OrderedSectionsConfig(SimpleConfig):
    """keeps the sections ordered

    Some features are disabled for keeping the data sane:

    * inheritance
    * merging
    """

    make_section = simple_section

    def merge(self, other):
        if hasattr(self, 'merged'):
            raise TypeError('cant merge to a OrderedSectionsConfig')
        else:
            self.update(other)
            self.merged = True

    def inherit(self, name):
        raise ValueError("OrderedSectionsConfig can't inherit")

    def sections(self):
        return sorted(SimpleConfig.sections(self), key=lambda v:v[1].line)


def _dump__kv(items):
    for item in sorted(items):
        yield '%s = %s\n'%item

def _dump__section(section):
    if isinstance(section, tuple):
        yield '\n[%s: %s]\n'%section
    else:
        yield '\n[%s]\n'%section

def _dump_w(data, writer):
    single = [ (k, v) for k, v in data.items() if not isinstance(v, dict)]
    writer(_dump__kv(single))
    for section, fields in data.sections():
        writer(_dump__section(section))
        writer(_dump__kv(fields.items()))

def _prepare_lines(lines):
    """prepares lines for handling the data"""
    for line, i in enumerate(lines):

        # line number is 1 based, enumerate 0 based
        line+=1
        i = i.strip()

        # ignore empty and whitespace
        if not i:
            continue

        # new section
        if i[0] == '[' and i[-1] == ']':
            section_name = i[1:-1]
            if ':' in section_name:
                prefix, name = section_name.split(':', 1)
                section_name = prefix.strip(), name.strip()
            yield line, section_name, None
        else:
            name, value = i.split('=', 1)
            name = name.strip()
            value = value.strip()
            yield line, name, value


def unmerge(data, base):
    """unmerges config data from base data
    :param data: current data
    :param base: base of the data
    :returns: required changes in order to merge base to data
    """
    result = type(data)()
    for k, v in data.items():
        b = base.get(k)
        if b is None:
            result[k] = v

        elif b != v:
            if isinstance(b, dict) and isinstance(v, dict):
                result[k] = unmerge(v, b)
            else:
                result[k] = v

    return result


