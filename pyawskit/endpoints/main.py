from __future__ import print_function, division

from pylogconf.core import setup
from pytconf.config import register_main, get_pytconf

from pyawskit.endpoints.group_default import register_group_default


def register_all_groups():
    # order of registration is important
    register_group_default()


@register_main()
def main():
    """
    Pytsv is you TSV Swiss Army Knife.
    """
    setup()
    register_all_groups()
    get_pytconf().config_arg_parse_and_launch()


if __name__ == '__main__':
    main()
