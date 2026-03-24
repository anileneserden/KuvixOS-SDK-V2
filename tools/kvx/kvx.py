#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parents[2]
INCLUDE_DIR = SDK_ROOT / "include"
LINKER = SDK_ROOT / "tools" / "linker_app.ld"
TEMPLATE_DIR = SDK_ROOT / "templates" / "basic-app"


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


def run(cmd):
    print("+", " ".join(str(x) for x in cmd))
    subprocess.check_call(cmd)


def cmd_init(args):
    if len(args) < 1:
        print("usage: kvx init <project-name>")
        return 1

    name = args[0]
    dst = Path(name)

    if dst.exists():
        print(f"error: {dst} already exists")
        return 1

    if not TEMPLATE_DIR.exists():
        print(f"error: template dir not found: {TEMPLATE_DIR}")
        return 1

    dst.mkdir(parents=True)

    shutil.copy(TEMPLATE_DIR / "kvx.toml", dst / "kvx.toml")
    shutil.copy(TEMPLATE_DIR / "main.cpp", dst / "main.cpp")
    shutil.copy(TEMPLATE_DIR / "app.json", dst / "app.json")

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
    ui = Path(cfg.get("ui", "app.json"))
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
    json_obj = obj_dir / "app_json.o"

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


def main():
    if len(sys.argv) < 2:
        print("usage: kvx <init|build> ...")
        return 1

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "init":
        return cmd_init(args)
    if cmd == "build":
        return cmd_build(args)

    print(f"unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())