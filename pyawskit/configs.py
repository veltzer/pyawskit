from pytconf.config import Config, ParamCreator


class ConfigName(Config):
    """
    Parameters to select the name of the config to launch
    """
    name = ParamCreator.create_str(help_string="index to use")


class ConfigFilter(Config):
    """
    Parameters to select if the use the filter or not
    """
    filter = ParamCreator.create_bool(
        default=True,
        help_string="use filter for the instances",
    )
