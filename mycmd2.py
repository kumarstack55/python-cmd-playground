#!/usr/bin/env python
import cmd2
from cmd2.parsing import Statement
from typing import Union
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


class StatementRecorder(object):
    def __init__(self):
        self._recording: bool = False
        self._statements: list[Statement] = list()

    def clear(self):
        self._statements = list()

    def start_record(self):
        self._recording = True

    def append_statement_if_recoding(self, statement: Statement):
        if self._recording:
            self._statements.append(statement)

    def stop_record(self):
        self._recording = False

    def get_statements(self):
        result = list()
        for s in self._statements:
            result.append(Statement.from_dict(s.to_dict()))
        return result


class MyCmdProperties(object):
    def __init__(self):
        self._last_repeatable_statement = None
        self._debug = False
        self._statement_recorder = StatementRecorder()

    @property
    def last_repeatable_statement(self) -> str:
        return self._last_repeatable_statement

    @last_repeatable_statement.setter
    def last_repeatable_statement(self, line: str):
        self._last_repeatable_statement = line

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, debug: bool):
        self._debug = debug

    @property
    def statement_recorder(self) -> StatementRecorder:
        return self._statement_recorder

    @statement_recorder.setter
    def statement_recorder(self, statement_recorder: StatementRecorder):
        self._statement_recorder = statement_recorder


class MyCmd(cmd2.Cmd):
    def __init__(self, **kwargs):
        self._my = MyCmdProperties()
        self.prompt = self._get_prompt('my')
        super().__init__(**kwargs)

    def _get_prompt(self, arg):
        return f'({arg})> '

    def _do_cmd_generic(self, arg):
        logger.debug('function=%s, arg=%s' % (get_caller_function(2), arg))

    def precmd(self, statement: Union[Statement, str]) -> Statement:
        logger.debug(f'function={get_caller_function()}, {statement=}')
        return super().precmd(statement)

    def _test_repeatable_cmd(self, statement: Statement):
        logger.debug(f'{statement.command=}')
        if statement.command == 'repeat':
            return False
        return True

    def postcmd(self, stop: bool, statement: Union[Statement, str]) -> bool:
        logger.debug(
            f'function={get_caller_function()}, {stop=}, {statement=}')

        if isinstance(statement, Statement):
            statement2 = statement
        else:
            statement2 = Statement(statement)
        if self._test_repeatable_cmd(statement2):
            self._my.last_repeatable_statement = statement2

        recorder = self._my.statement_recorder
        recorder.append_statement_if_recoding(statement2)

        return super().postcmd(stop, statement)

    def do_repeat(self, arg):
        '''
        Repeat a non-empty command.
        '''
        self._do_cmd_generic(arg)

        # Repeat a non-empty command.
        logger.debug(f'{self._my.last_repeatable_statement=}')
        if self._my.last_repeatable_statement is not None:
            line = self._my.last_repeatable_statement.raw
            logger.debug(f'{line=}')
            self.onecmd_plus_hooks(line)

    def do_x_cmd_a(self, arg):
        self._do_cmd_generic(arg)
        print("cmd_a is executed")

    def do_x_cmd_b(self, arg):
        self._do_cmd_generic(arg)
        print("cmd_b is executed")

    def do_x_record_print(self, arg):
        self._do_cmd_generic(arg)
        for s in self._my.statement_recorder.get_statements():
            line = s.raw
            print(f'{line=}')

    def do_record_start(self, arg):
        '''
        Start statement recording.
        '''
        self._do_cmd_generic(arg)
        self._my.statement_recorder.start_record()

    def do_record_stop(self, arg):
        '''
        Stop statement recording.
        '''
        self._do_cmd_generic(arg)
        self._my.statement_recorder.stop_record()

    def do_record_clear(self, arg):
        '''
        Clear recorded statements.
        '''
        self._do_cmd_generic(arg)
        self._my.statement_recorder.clear()

    def do_record_play(self, arg):
        '''
        Play recorded statements.
        '''
        self._do_cmd_generic(arg)

        recorder = self._my.statement_recorder
        for s in recorder.get_statements():
            line = s.raw
            logger.debug(f'{line=}')
            self.onecmd_plus_hooks(line)

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
        Set prompt.
        '''
        self._do_cmd_generic(arg)
        self.prompt = self._get_prompt(arg)


def clean_up():
    logger.debug(f'function={get_caller_function(1)}')


def main():
    c = MyCmd()
    c.cmdloop()
    clean_up()


if __name__ == '__main__':
    main()
