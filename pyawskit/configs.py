from pytconf import Config, ParamCreator


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


class ConfigWork(Config):
    """
    Parameters to control the actualy device work
    """
    device_file = ParamCreator.create_str(
        default="/dev/md0",
        help_string="device to use",
    )
    mount_point = ParamCreator.create_str(default="/mnt/raid0", help_string="mount point")
    mdadm_config_file = ParamCreator.create_str(default="/etc/mdadm/mdadm.conf", help_string="mdadm config file")
    mdadm_binary = ParamCreator.create_str(default="/sbin/mdadm", help_string="mdam tool")
    fstab_filename = ParamCreator.create_str(default="/etc/fstab", help_string="fstab filename")
    file_system_type = ParamCreator.create_str(default="ext4", help_string="file system type")
    name_of_raid_device = ParamCreator.create_str(default="MY_RAID", help_string="name of raid device")
    start_stop_queue = ParamCreator.create_bool(default=False, help_string="do start stop queue")
    write_etc_mdadm = ParamCreator.create_bool(default=False, help_string="write /etc/mdadm")
    add_line_to_fstab = ParamCreator.create_bool(default=False, help_string="add line to /etc/fstab")


class ConfigAwsCodeartifactNpm(Config):
    env_npm_domain = ParamCreator.create_str(help_string="env npm domain")
    env_npm_domain_owner = ParamCreator.create_str(help_string="env npm domain owner")
    env_npm_repository = ParamCreator.create_str(help_string="env npm repository")


class ConfigAwsCodeartifactPip(Config):
    env_pip_domain = ParamCreator.create_str(help_string="env pip domain")
    env_pip_domain_owner = ParamCreator.create_str(help_string="env pip domain owner")
    env_pip_repository = ParamCreator.create_str(help_string="env pip repository")


class ConfigRoleDuplicate(Config):
    from_role = ParamCreator.create_str(help_string="from role name")
    to_role = ParamCreator.create_str(help_string="to role name")


class ConfigRole(Config):
    role = ParamCreator.create_str(help_string="role name")
