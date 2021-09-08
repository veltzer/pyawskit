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
    mdadm_config_file = ParamCreator.create_str(default='/etc/mdadm/mdadm.conf', help_string="mdadm config file")
    mdadm_binary = "/sbin/mdadm"
    fstab_filename = "/etc/fstab"
    file_system_type = "ext4"
    name_of_raid_device = "MY_RAID"
    start_stop_queue = False
    write_etc_mdadm = False
    add_line_to_fstab = False
