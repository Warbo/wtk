# Copyright

from . import VCSBackend as _VCSBackend
from . import utils as _utils


class GitBackend (_VCSBackend):
    name = 'Git'

    @staticmethod
    def _git_cmd(*args):
        status,stdout,stderr = _utils.invoke(['git'] + list(args))
        return stdout.rstrip('\n')

    def __init__(self, **kwargs):
        super(GitBackend, self).__init__(**kwargs)
        self._version = self._git_cmd('--version').split(' ')[-1]
        if self._version.startswith('1.5.'):
            # Author name <author email>
            self._author_format = '--pretty=format:%an <%ae>'
            self._year_format = ['--pretty=format:%ai']  # Author date
            # YYYY-MM-DD HH:MM:SS Z
            # Earlier versions of Git don't seem to recognize --date=short
        else:
            self._author_format = '--pretty=format:%aN <%aE>'
            self._year_format = ['--pretty=format:%ad',  # Author date
                                 '--date=short']         # YYYY-MM-DD

    def _years(self, filename=None):
        args = ['log'] + self._year_format
        if filename is not None:
            args.extend(['--follow'] + [filename])
        output = self._git_cmd(*args)
        if self._version.startswith('1.5.'):
            output = '\n'.join([x.split()[0] for x in output.splitlines()])
        years = set(int(line.split('-', 1)[0]) for line in output.splitlines())
        return years

    def _authors(self, filename=None):
        args = ['log', self._author_format]
        if filename is not None:
            args.extend(['--follow', filename])
        output = self._git_cmd(*args)
        authors = set(output.splitlines())
        return authors

    def is_versioned(self, filename):
        output = self._git_cmd('log', '--follow', filename)
        if len(output) == 0:
            return False
        return True
