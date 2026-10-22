"""Check (and optionally install) the Python libraries a campaign needs, so no agent loses its first minutes on a
missing import (references/tempo.md, rule 6.4).
Usage:  python check_env.py --variant math|ml|software|algorithm [--install]
Exit code 0 when everything imports (after --install, if given), 1 otherwise."""
import argparse, importlib.util, subprocess, sys

# import name -> pip name; pyyaml is needed by the far-analogy scripts (No. 7) in every variant
NEEDS = {
    "math": {"yaml": "pyyaml", "numpy": "numpy", "scipy": "scipy", "sympy": "sympy"},
    "ml": {"yaml": "pyyaml", "numpy": "numpy", "scipy": "scipy", "sklearn": "scikit-learn"},
    "algorithm": {"yaml": "pyyaml", "numpy": "numpy", "scipy": "scipy"},
    "software": {"yaml": "pyyaml"},
}


def missing(variant):
    return {m: p for m, p in NEEDS[variant].items() if importlib.util.find_spec(m) is None}


def check(variant, install=False):
    """Return the pip names still missing after an optional install."""
    miss = missing(variant)
    if miss and install:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", *miss.values()], check=False)
        importlib.invalidate_caches()
        miss = missing(variant)
    return sorted(miss.values())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--variant", required=True, choices=sorted(NEEDS))
    ap.add_argument("--install", action="store_true")
    a = ap.parse_args(argv)
    miss = check(a.variant, a.install)
    if miss:
        print("missing libraries:", " ".join(miss))
        print(f'install: "{sys.executable}" -m pip install ' + " ".join(miss))
        return 1
    print("environment ok:", ", ".join(sorted(NEEDS[a.variant].values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
