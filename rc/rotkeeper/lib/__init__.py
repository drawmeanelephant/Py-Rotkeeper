from . import init, render, assets

def get_commands():
    """
    Return a list of (command_name, add_parser_func) for dynamic CLI registration.
    """
    return [
        ("init", init.add_parser),
        ("render", render.add_parser),
        ("assets", assets.add_parser),
    ]
