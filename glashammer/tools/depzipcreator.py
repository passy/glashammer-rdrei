
import os, tempfile, shutil, subprocess, uuid, sys


OWD = os.path.abspath(os.getcwd())

GH_URL = 'http://bitbucket.org/aafshar/glashammer-main'
J2_URL = 'http://dev.pocoo.org/hg/jinja2-main'
WZ_URL = 'http://dev.pocoo.org/hg/werkzeug-main'
SJ_URL = 'http://simplejson.googlecode.com/svn/trunk/'

os.environ['PYTHONPATH'] = '../lib/'

class ZipCreator(object):

    def __init__(self):
        self.setup()

    def setup(self):
        self.wd = tempfile.mkdtemp(prefix='gh_deps_zip_')
        os.chdir(self.wd)

    def run(self):
        for u in [GH_URL]:
            self.hg_get(u)
        for u in [J2_URL, WZ_URL]:
            self.hg_get_st(u)
        for u in [SJ_URL]:
            self.sj_get(u)

        os.system('rm -rf lib/*.egg-info lib/usr')

        os.chdir('lib')
        os.system('zip -r glashammer_deps.zip *')
        shutil.copy('glashammer_deps.zip', os.path.join(OWD, 'glashammer_deps.zip'))

    def teardown(self):
        shutil.rmtree(self.wd)

    def sj_get(self, url):
        name = str(uuid.uuid1())
        subprocess.Popen(['svn', 'co', url, name]).communicate()
        os.makedirs('lib/simplejson')
        os.system('cp -R %s/simplejson/*.py lib/simplejson' % name)

    def hg_get(self, url):
        name = str(uuid.uuid1())
        subprocess.Popen(['hg', 'clone', url, name]).communicate()
        subprocess.Popen(['python', 'setup.py', 'install',
                '--install-lib=../lib',
                '--root=../lib',
                '--no-compile',
                ],
            cwd=name).communicate()

    def hg_get_st(self, url):
        name = str(uuid.uuid1())
        subprocess.Popen(['hg', 'clone', url, name]).communicate()
        subprocess.Popen(['python', 'setup.py', 'install',
                '--install-lib=../lib',
                '--root=../lib',
                '--no-compile',
                '--single-version-externally-managed',
                ],
            cwd=name).communicate()

def main():
    z = ZipCreator()
    z.run()
    os.system('ls -alh ' + z.wd + '/lib/')
    z.teardown()
    os.chdir(OWD)

if __name__ == '__main__':
    main()

