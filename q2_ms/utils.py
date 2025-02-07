import importlib
import os
import subprocess

EXTERNAL_CMD_WARNING = (
    "Running external command line application(s). "
    "This may print messages to stdout and/or stderr.\n"
    "The command(s) being run are below. These commands "
    "cannot be manually re-run as they will depend on "
    "temporary files that no longer exist."
)


def run_command(cmd, cwd, verbose=True, env=None):
    if verbose:
        print(EXTERNAL_CMD_WARNING)
        print("\nCommand:", end=" ")
        print(" ".join(cmd), end="\n\n")
    subprocess.run(cmd, check=True, cwd=cwd, env=env)


def run_r_script(params, script_name, package_name):
    script_path = str(importlib.resources.files("q2_ms") / f"assets/{script_name}.R")
    cmd = ["/usr/local/bin/Rscript", "--vanilla", script_path]

    for key, value in params.items():
        if value is not None:
            cmd.extend([f"--{key}", str(value)])

    # Add /usr/local/bin to PATH to use system installation of Rscript
    env = os.environ.copy()
    env["PATH"] = "/usr/local/bin:" + env["PATH"]

    # Unset Conda-related R variables to prevent it from overriding the system R library
    for var in ["R_LIBS", "R_LIBS_USER", "R_HOME", "CONDA_PREFIX"]:
        env.pop(var, None)

    try:
        run_command(cmd, verbose=True, cwd=None, env=env)
    except subprocess.CalledProcessError as e:
        raise Exception(
            f"An error was encountered while running {package_name}, "
            f"(return code {e.returncode}), please inspect "
            "stdout and stderr to learn more."
        )
