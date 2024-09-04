import traceback as tb


def print_debug(e):
    print("".join(tb.format_exception(None, e, e.__traceback__)))
