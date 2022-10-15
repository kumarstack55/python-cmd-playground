#!/usr/bin/env python
import cmd
import inspect
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_caller_function(depth=1):
    return inspect.stack()[depth].function


class MyCmdProperties(object):
    def __init__(self):
        self._last_line = None
        self._debug = False

    @property
    def last_line(self) -> str:
        return self._last_line

    @last_line.setter
    def last_line(self, line: str):
        self._last_line = line

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, debug: bool):
        self._debug = debug


class MyCmd(cmd.Cmd):
    def __init__(self, **kwargs):
        self._my = MyCmdProperties()
        self.prompt = self._get_prompt('my')
        super().__init__(**kwargs)

    def _get_prompt(self, arg):
        return f'({arg})> '

    def _do_cmd_generic(self, arg):
        logger.debug('function=%s, arg=%s' % (get_caller_function(2), arg))

    def onecmd(self, line):
        logger.debug(f'function={get_caller_function()}, {line=}')
        return super().onecmd(line)

    def emptyline(self):
        # Override the method to prevent repeating non-empty commands.
        logger.debug('function=%s' % (get_caller_function()))

    def default(self, line):
        logger.debug(f'function={get_caller_function()}, {line=}')
        return super().default(line)

    def completedefault(self, text, line, begidx, endidx):
        logger.debug(
                f'function={get_caller_function()}, {text=}, {line=}, ' +
                f'{endidx=}')
        return super().completedefault(text, line, begidx, endidx)

    def precmd(self, line):
        logger.debug(f'function={get_caller_function()}, {line=}')
        if line == '.':
            line = 'dot'
        return line

    def _test_repeatable_cmd(self, line):
        cmd, arg, line = self.parseline(line)
        if cmd == 'dot':
            return False
        return True

    def postcmd(self, stop, line):
        logger.debug(f'function={get_caller_function()}, {stop=}, {line=}')

        if self._test_repeatable_cmd(line):
            self._my.last_line = line
        return super().postcmd(stop, line)

    def preloop(self):
        logger.debug('function=%s' % (get_caller_function()))
        return super().preloop()

    def postloop(self):
        logger.debug('function=%s' % (get_caller_function()))
        return super().postloop()

    def do_dot(self, arg):
        '''
        Repeat a non-empty command.
        '''
        self._do_cmd_generic(arg)

        # Repeat a non-empty command.
        if self._my.last_line:
            return self.onecmd(self._my.last_line)

    def do_cmd_a(self, arg):
        self._do_cmd_generic(arg)

    def do_cmd_b(self, arg):
        self._do_cmd_generic(arg)

    def do_record_start(self, arg):
        self._do_cmd_generic(arg)

    def do_record_stop(self, arg):
        self._do_cmd_generic(arg)

    def do_record_play(self, arg):
        self._do_cmd_generic(arg)

    def do_debug(self, arg):
        '''
        Toggle debug mode.
        '''
        self._do_cmd_generic(arg)

        self._my.debug = not self._my.debug
        print(f'debug: {self._my.debug}')

        level = logging.DEBUG if self._my.debug else logging.WARNING
        handler.setLevel(level)

    def do_prompt(self, arg):
        '''
        Toggle debug mode.
        '''
        self._do_cmd_generic(arg)
        self.prompt = self._get_prompt(arg)

    def do_exit(self, arg):
        self._do_cmd_generic(arg)
        return True


def clean_up():
    logger.debug(f'function={get_caller_function(1)}')


def main():
    try:
        MyCmd().cmdloop()
    except KeyboardInterrupt:
        print()
    finally:
        clean_up()


if __name__ == '__main__':
    main()
