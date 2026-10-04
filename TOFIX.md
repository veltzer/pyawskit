# TOFIX

Findings from a code scan on 2026-10-04.

## High

- `src/pyawskit/main.py:64` - the `compress_s3_folder` endpoint cannot work: it uses a hard-coded placeholder bucket (`"bucket_name"`, `"flipkart/"`, lines 73-75); `object_exists()` (line 89) calls `head_object` on a boto3 *resource*, which has no such method (it is a client method, `src/pyawskit/utils.py:60`); the pool job `compress_one_file` is a `pass` stub (`src/pyawskit/utils.py:96`) while the real worker `process_one_file` is never called; and `pool.join()` (line 95) without `pool.close()` raises `ValueError: Pool is still running` (reproduced). Either rewrite it with real config params, a boto3 client, `process_one_file` and `close()`+`join()`, or drop the endpoint.
- `src/pyawskit/main.py:235` - the `prep_machine` endpoint takes a required `name` argument, but pytconf invokes endpoints with no arguments (`select.function()` in pytconf/config.py), so it always fails with TypeError. Take the host name from a Config class or free args.
- `src/pyawskit/aws_ecr_login_code.py:33` - `docker login` is skipped whenever `~/.docker/config.json` already has an entry for the registry. ECR tokens expire after 12h, so after the first login the stale entry makes every later run (cached or freshly fetched token) skip the login, and pulls fail with an expired token. Always log in when a new token is fetched (or compare against the cached expiration), not based on the presence of an `auths` key.
- `src/pyawskit/roles.py:64` - `role_delete` calls `delete_instance_profile` before `remove_role_from_instance_profile` (line 68); IAM refuses to delete an instance profile that still contains a role (DeleteConflict), so deleting any role with an instance profile fails. Swap the two calls.

## Medium

- `src/pyawskit/aws_ecr_login_code.py:38` - the ECR password is passed as `docker login --password <token>`, exposing it in the process list (and docker itself warns against it). Use `--password-stdin` and feed the token via `input=`.
- `src/pyawskit/utils.py:41` - `gzip_file_process` runs `f"gzip < {file_in} > {file_out}"` with `shell=True`; the names come from S3 object keys (`process_one_file`), so a key containing shell metacharacters is executed. Open the files in Python and pass them as stdin/stdout to `["gzip"]`, or use `gzip_file()` which already exists.
- `src/pyawskit/main.py:114` - `copy_to_machine` asserts `len(sys.argv) == 2`, but it is run as `pyawskit copy_to_machine <host>` (argv length 3), so the assertion always fails. Use pytconf free args (`allow_free_args=True` + `get_free_args()`) or a Config param.
- `src/pyawskit/aws_ecr_login_code.py:72` - `logout()` runs `docker login` instead of `docker logout`. It is currently unused; fix or remove it.
- `src/pyawskit/aws_codeartifact_npm_env_config_code.py:90` - `d_short_url` is only assigned when the endpoint starts with `https:`; otherwise line 95 raises UnboundLocalError. Derive it unconditionally (e.g. strip the scheme with urlparse). The module docstring (line 2) also says "url for pip" in the npm module.
- `pyproject.toml:50` - `docker-py` is the long-deprecated old name of the `docker` package and is never imported (only in a commented-out line, `src/pyawskit/aws_ecr_login_code.py:12`); `pyfakeuse` (line 39) and `ujson` (line 45) are also never imported anywhere in `src/` or `tests/`. Remove the unused dependencies and refresh uv.lock.
- `src/pyawskit/common.py:214` - `update_ssh_config` writes `~/.ssh/config.d/99_dynamic.conf` (line 247) without creating `~/.ssh/config.d`, so `generate_ssh_config` and `launch_machine` crash with FileNotFoundError on a machine without that directory. Create the parent directory first (already noted as wanted in `doc/TODO.txt:3`).

## Low

- `src/pyawskit/os_utils.py:29` - module is never imported, and `detect_os` is broken: on Ubuntu it sets `os_data` (line 38) but leaves `os_type` None so it exits with "could not detect the os"; on Amazon Linux it sets `os_type` (line 43) but not `os_data`, so `is_os_type` raises KeyError. The package list also names gone Ubuntu packages (`python-pip`, `python-dev`). Delete the module or fix it.
- `src/pyawskit/devices.py:73` - `mount_disks` builds `folder = f"/mnt/{disk}"` from a full device path, giving `/mnt//dev/xvdb`; use the basename. The log lines at 40 and 46 print `ConfigWork.device_file` instead of the `disk` being checked. Note `mount_disks`/`unify_disks` are not registered as endpoints, so this module is currently unreachable.
- `src/pyawskit/main.py:134` - `generate_etc_hosts` and `generate_ssh_config` (line 151) docstrings say they update `~/.aws/config` and that `.pem` files live in `~/.aws/keys`; the code writes `/etc/hosts` / `~/.ssh/config.d/99_dynamic.conf` and uses `~/.pyawskit/keys/` (`src/pyawskit/common.py:234`). Fix the docstrings.
- `doc/TODO.txt:24` - refers to `scripts/from_mine.sh` and `prep_machine.sh` (there is no `scripts/` directory) and to per-script names like `pyawskit_launch_machine` that were replaced by `pyawskit <endpoint>` subcommands; update or prune the TODO list.
