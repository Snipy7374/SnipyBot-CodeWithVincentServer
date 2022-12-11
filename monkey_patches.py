import re
import sys

from os.path import basename, splitext
from threading import current_thread
from multiprocessing import current_process


from loguru import _logger
from loguru._get_frame import get_frame
from loguru._datetime import aware_now
from loguru._recattrs import (
    RecordException,
    RecordFile,
    RecordLevel,
    RecordThread,
    RecordProcess,
)
from loguru._contextvars import ContextVar
from loguru._colorizer import Colorizer
from loguru._file_sink import FileSink


__all__ = ("MonkeyPatchedLogger",)

context = ContextVar("loguru_context", default={})
start_time = aware_now()


class MonkeyPatchedLogger(_logger.Logger):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _log(
        self,
        level_id,
        static_level_no,
        from_decorator,
        options,
        message,
        args,
        kwargs
    ):
        core = self._core

        if not core.handlers:
            return

        (exception, depth, record, lazy, colors, raw, capture, patcher, extra) = options  # noqa: E501

        frame = get_frame(depth + 2)

        try:
            name = frame.f_globals["__name__"]  # type: ignore
        except KeyError:
            name = None

        try:
            if not core.enabled[name]:
                return
        except KeyError:
            enabled = core.enabled
            if name is None:
                status = core.activation_none
                enabled[name] = status
                if not status:
                    return
            else:
                dotted_name = name + "."
                for dotted_module_name, status in core.activation_list:
                    if dotted_name[: len(dotted_module_name)] == dotted_module_name:  # noqa: E501
                        if status:
                            break
                        enabled[name] = False
                        return
                enabled[name] = True

        current_datetime = aware_now()

        if level_id is None:
            level_icon = " "
            level_no = static_level_no
            level_name = "Level %d" % level_no
        else:
            try:
                level_name, level_no, _, level_icon = core.levels[level_id]
            except KeyError:
                raise ValueError("Level '%s' does not exist" % level_id) from None  # noqa: E501

        if level_no < core.min_level:
            return

        code = frame.f_code  # type: ignore
        file_path = code.co_filename
        file_name = basename(file_path)
        thread = current_thread()
        process = current_process()
        elapsed = current_datetime - start_time

        if exception:
            if isinstance(exception, BaseException):
                type_, value, traceback = (
                    type(exception),
                    exception,
                    exception.__traceback__,
                )
            elif isinstance(exception, tuple):
                type_, value, traceback = exception
            else:
                type_, value, traceback = sys.exc_info()
            exception = RecordException(type_, value, traceback)
        else:
            exception = None

        log_record = {
            "elapsed": elapsed,
            "exception": exception,
            "extra": {**core.extra, **context.get(), **extra},
            "file": RecordFile(file_name, file_path),
            "function": code.co_name,
            "level": RecordLevel(level_name, level_no, level_icon),
            "line": frame.f_lineno,  # type: ignore
            "message": str(message),
            "module": splitext(file_name)[0],
            "name": name,
            "process": RecordProcess(process.ident, process.name),
            "thread": RecordThread(thread.ident, thread.name),
            "time": current_datetime,
        }

        if lazy:
            args = [arg() for arg in args]
            kwargs = {key: value() for key, value in kwargs.items()}

        if capture and kwargs:
            log_record["extra"].update(kwargs)

        if record:
            if "record" in kwargs:
                raise TypeError(
                    "The message can't be formatted: 'record' shall not be used as a keyword "  # noqa: E501
                    "argument while logger has been configured with '.opt(record=True)'"  # noqa: E501
                )
            kwargs.update(record=log_record)

        if colors:
            if args or kwargs:
                colored_message = Colorizer.prepare_message(message, args, kwargs)  # noqa: E501
            else:
                colored_message = Colorizer.prepare_simple_message(str(message))  # noqa: E501
            log_record["message"] = colored_message.stripped
        elif args or kwargs:
            colored_message = None
            log_record["message"] = message.format(*args, **kwargs)
        else:
            colored_message = None

        if core.patcher:
            core.patcher(log_record)

        if patcher:
            patcher(log_record)

        for handler in core.handlers.values():
            if isinstance(handler._sink, FileSink):
                actual_msg = log_record["message"]
                log_record["message"] = self._escape_ansi_codes(actual_msg)
                handler.emit(log_record, level_id, from_decorator, raw, None)
                return
            handler.emit(log_record, level_id, from_decorator, raw, colored_message)  # noqa: E501

    def _escape_ansi_codes(self, string: str) -> str:
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", string)


def apply_monkey_patch():
    _logger.Logger._log = MonkeyPatchedLogger._log  # type: ignore
    _logger.Logger._escape_ansi_codes = MonkeyPatchedLogger._escape_ansi_codes  # type: ignore  # noqa: E501
