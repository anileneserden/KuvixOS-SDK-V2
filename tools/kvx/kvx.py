#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

# ==========================
# KVX META
# ==========================
KVX_VERSION = "0.1.1"
VERSION_URL = "https://sdk.kuvixos.com.tr/version.json"

# ==========================
# PATHS
# ==========================
SDK_ROOT = Path(__file__).resolve().parents[2]
INCLUDE_DIR = SDK_ROOT / "include"
LINKER = SDK_ROOT / "tools" / "linker_app.ld"
TEMPLATE_DIR = SDK_ROOT / "templates" / "basic-app"

CONFIG_DIR = Path.home() / ".config" / "kvx"
CONFIG_FILE = CONFIG_DIR / "config.toml"
DEFAULT_WORKSPACE = Path.home() / "KuvixProjects"

# ==========================
# COLORS
# ==========================
CLR_RESET = "\033[0m"
CLR_RED = "\033[31m"
CLR_GREEN = "\033[32m"
CLR_YELLOW = "\033[33m"
CLR_CYAN = "\033[36m"


# ==========================
# UTILS
# ==========================
def run(cmd):
    print("+", " ".join(str(x) for x in cmd))
    subprocess.check_call(cmd)


def read_simple_toml(path: Path):
    data = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip().strip('"')
    return data


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def read_user_config():
    if not CONFIG_FILE.exists():
        return {}
    return read_simple_toml(CONFIG_FILE)


def write_user_config(data):
    ensure_config_dir()
    lines = []
    for k, v in data.items():
        lines.append(f'{k} = "{v}"')
    CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def expand_user_path(p: str) -> Path:
    return Path(os.path.expanduser(p)).resolve()


def get_workspace_path():
    cfg = read_user_config()
    ws = cfg.get("workspace")
    if ws:
        return expand_user_path(ws)
    return DEFAULT_WORKSPACE


def parse_version(v: str):
    parts = v.strip().split(".")
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])


def fetch_json(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"kvx/{KVX_VERSION}"
        },
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ==========================
# HELP / VERSION
# ==========================
def print_help():
    print(f"""
KuvixOS SDK CLI (kvx {KVX_VERSION})

Usage:
  kvx init <name> [--here]
  kvx build
  kvx config get <key>
  kvx config set <key> <value>
  kvx version
  kvx update-check

Options:
  --help       Show this help
  --version    Show kvx version
""")


def print_version():
    print(f"kvx {KVX_VERSION}")


# ==========================
# COMMANDS
# ==========================
def cmd_config(args):
    if len(args) < 1:
        print("usage:")
        print("  kvx config get <key>")
        print("  kvx config set <key> <value>")
        return 1

    sub = args[0]

    if sub == "get":
        if len(args) < 2:
            print("usage: kvx config get <key>")
            return 1

        key = args[1]
        cfg = read_user_config()

        if key == "workspace":
            value = cfg.get("workspace", str(DEFAULT_WORKSPACE))
            print(value)
            return 0

        print(f"error: unknown config key: {key}")
        return 1

    if sub == "set":
        if len(args) < 3:
            print("usage: kvx config set <key> <value>")
            return 1

        key = args[1]
        value = args[2]

        cfg = read_user_config()

        if key == "workspace":
            ws = expand_user_path(value)
            ws.mkdir(parents=True, exist_ok=True)
            cfg["workspace"] = str(ws)
            write_user_config(cfg)
            print(f"workspace set to {ws}")
            return 0

        print(f"error: unknown config key: {key}")
        return 1

    print(f"error: unknown config command: {sub}")
    return 1


def cmd_init(args):
    if len(args) < 1:
        print("usage: kvx init <project-name> [--here]")
        return 1

    name = None
    create_here = False

    for arg in args:
        if arg == "--here":
            create_here = True
        elif name is None:
            name = arg

    if not name:
        print("usage: kvx init <project-name> [--here]")
        return 1

    if not TEMPLATE_DIR.exists():
        print(f"error: template dir not found: {TEMPLATE_DIR}")
        return 1

    if create_here:
        dst = Path.cwd() / name
    else:
        workspace = get_workspace_path()
        workspace.mkdir(parents=True, exist_ok=True)
        dst = workspace / name

    if dst.exists():
        print(f"error: {dst} already exists")
        return 1

    dst.mkdir(parents=True)

    shutil.copy(TEMPLATE_DIR / "kvx.toml", dst / "kvx.toml")
    shutil.copy(TEMPLATE_DIR / "main.cpp", dst / "main.cpp")
    shutil.copy(TEMPLATE_DIR / "layout.json", dst / "layout.json")

    text = (dst / "kvx.toml").read_text(encoding="utf-8")
    text = text.replace('name = "hello"', f'name = "{name}"')
    (dst / "kvx.toml").write_text(text, encoding="utf-8")

    print(f"initialized {dst}")
    return 0


def cmd_build(args):
    manifest = Path("kvx.toml")
    if not manifest.exists():
        print("error: kvx.toml not found")
        return 1

    cfg = read_simple_toml(manifest)

    entry = Path(cfg.get("entry", "main.cpp"))
    ui = Path(cfg.get("ui", "layout.json"))
    output = Path(cfg.get("output", "build/app.kef"))

    if not entry.exists():
        print(f"error: entry file not found: {entry}")
        return 1

    if not ui.exists():
        print(f"error: ui file not found: {ui}")
        return 1

    if not LINKER.exists():
        print(f"error: linker script not found: {LINKER}")
        return 1

    build_dir = Path("build")
    obj_dir = build_dir / "obj"
    obj_dir.mkdir(parents=True, exist_ok=True)

    cpp_obj = obj_dir / "main.o"
    json_obj = obj_dir / "layout_json.o"

    cxx = os.environ.get("CXX", "g++")
    objcopy = os.environ.get("OBJCOPY", "objcopy")

    run([
        cxx,
        "-m32",
        "-ffreestanding",
        "-O2",
        "-Wall",
        "-Wextra",
        "-fno-pie",
        "-fno-exceptions",
        "-fno-rtti",
        "-nostdlib",
        "-nostartfiles",
        "-I", str(INCLUDE_DIR),
        "-std=c++17",
        "-c", str(entry),
        "-o", str(cpp_obj),
    ])

    run([
        objcopy,
        "-I", "binary",
        "-O", "elf32-i386",
        "-B", "i386",
        str(ui),
        str(json_obj),
    ])

    output.parent.mkdir(parents=True, exist_ok=True)

    run([
        cxx,
        "-m32",
        "-nostdlib",
        "-ffreestanding",
        "-fno-pie",
        "-Wl,-T," + str(LINKER),
        "-Wl,--build-id=none",
        "-Wl,--gc-sections",
        "-o", str(output),
        str(cpp_obj),
        str(json_obj),
    ])

    print(f"built {output}")
    return 0


def cmd_update_check(args):
    (void_args := args)  # unused placeholder for symmetry
    try:
        data = fetch_json(VERSION_URL)
    except Exception as e:
        print(f"{CLR_RED}update check failed{CLR_RESET}: {e}")
        return 1

    latest = str(data.get("latest", "")).strip()
    channel = str(data.get("channel", "stable")).strip()
    download_url = str(data.get("download_url", "")).strip()

    if not latest:
        print(f"{CLR_RED}update check failed{CLR_RESET}: invalid version.json")
        return 1

    current_v = parse_version(KVX_VERSION)
    latest_v = parse_version(latest)

    print(f"current: {KVX_VERSION}")
    print(f"latest : {latest}")
    print(f"channel: {channel}")

    if current_v == latest_v:
        print(f"{CLR_GREEN}kvx is up to date{CLR_RESET}")
        return 0

    if current_v < latest_v:
        print(f"{CLR_YELLOW}update available{CLR_RESET}")
        if download_url:
            print(f"download: {download_url}")
        return 0

    print(f"{CLR_CYAN}local version is newer than published version{CLR_RESET}")
    return 0

def cmd_update(args):
    print("checking for updates...")

    try:
        data = fetch_json(VERSION_URL)
    except Exception as e:
        print(f"{CLR_RED}failed to fetch version info{CLR_RESET}: {e}")
        return 1

    latest = str(data.get("latest", "")).strip()

    if not latest:
        print("invalid version data")
        return 1

    current_v = parse_version(KVX_VERSION)
    latest_v = parse_version(latest)

    if current_v >= latest_v:
        print(f"{CLR_GREEN}already up to date{CLR_RESET}")
        return 0

    print(f"{CLR_YELLOW}updating kvx → {latest}{CLR_RESET}")

    try:
        subprocess.check_call([
            "bash", "-c",
            "curl -fsSL https://sdk.kuvixos.com.tr/install.sh | bash"
        ])
    except subprocess.CalledProcessError:
        print(f"{CLR_RED}update failed{CLR_RESET}")
        return 1

    print(f"{CLR_GREEN}update complete ✔{CLR_RESET}")
    print("restart your terminal if needed")

    return 0

# ==========================
# MAIN
# ==========================
def main():
    if len(sys.argv) < 2:
        print_help()
        return 1

    cmd = sys.argv[1]
    args = sys.argv[2:]

    # Global flags
    if cmd in ("--help", "-h"):
        print_help()
        return 0

    if cmd in ("--version", "-v"):
        print_version()
        return 0

    if cmd == "version":
        print_version()
        return 0

    # Commands
    if cmd == "init":
        return cmd_init(args)

    if cmd == "build":
        return cmd_build(args)

    if cmd == "config":
        return cmd_config(args)

    if cmd == "update-check":
        return cmd_update_check(args)

    if cmd == "update":
        return cmd_update(args)

    print(f"unknown command: {cmd}")
    print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())