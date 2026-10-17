"""Read JSON engineering inputs and print a guarded calculation report."""
import argparse
import json
from pathlib import Path

from engineering_calculations import calculate_all


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="?", type=Path, default=Path(__file__).with_name("calculation-inputs.json"))
    args = parser.parse_args()
    try:
        config = json.loads(args.inputs.read_text(encoding="utf-8"))
        result = calculate_all(config)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"Invalid engineering input: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
