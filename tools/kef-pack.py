#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        print("usage: kef-pack.py <input.json> <output.kef>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    data = input_path.read_text(encoding="utf-8")

    # İlk sürüm: .kef aslında JSON içeriği taşıyan düz metin dosyası
    # Böylece loader tarafında uzantı .kef olsa da mevcut JSON parser ile açabiliriz.
    output_path.write_text(data, encoding="utf-8")

    print(f"[kef-pack] wrote {output_path}")

if __name__ == "__main__":
    main()