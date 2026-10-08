"""Build and sign latest.json (update manifest v2) for one release.

Usage: sign-manifest.py <version> <assets-dir> <public-key-hex-file> <output-dir>

Every file named Zalohuj-<file-version>-<platform>.<ext> in <assets-dir> becomes
one platform entry; <file-version> is the version with "+" replaced by ".",
because GitHub cannot serve an asset whose name holds a "+". The Ed25519 PEM arrives in ZALOHUJ_SIGNING_PEM and is held in
memory only. The payload format must match SignedRelease in
zalohuj-ui/src/update.rs.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

MAX_ASSET_SIZE = 2 * 1024 * 1024 * 1024
VERSION_RE = re.compile(r"\d+\.\d+\.\d+\+\d+")
RELEASE_URL = "https://github.com/version-two/zalohuj-releases/releases/download"
UPDATER_ASSET = {
    "windows-x86_64": "-setup.exe",
    "darwin-aarch64": ".app.tar.gz",
    "darwin-x86_64": ".app.tar.gz",
    "linux-x86_64": ".AppImage",
    "linux-aarch64": ".AppImage",
}


def payload(version: str, platform: str, digest: str, size: int) -> bytes:
    return f"zalohuj-update-v2\n{version}\n{platform}\n{digest}\n{size}\n".encode("utf-8")


def main() -> None:
    version, assets_dir, pin_file, output_dir = sys.argv[1:5]
    assets = Path(assets_dir)
    out = Path(output_dir)
    if not VERSION_RE.fullmatch(version):
        raise SystemExit(f"invalid release version: {version!r}")
    pin = Path(pin_file).read_text(encoding="ascii").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", pin):
        raise SystemExit("update-public-key.hex must hold 32 bytes in hex")

    pem = os.environ.get("ZALOHUJ_SIGNING_PEM", "").strip()
    if not pem:
        raise SystemExit("ZALOHUJ_SIGNING_PEM is not set")
    key = serialization.load_pem_private_key(pem.encode("ascii"), None)
    if not isinstance(key, Ed25519PrivateKey):
        raise SystemExit("release signing key must be Ed25519")
    derived = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
    if derived != pin:
        raise SystemExit("signing key does not match the pinned update public key")

    file_version = version.replace("+", ".")
    platforms = {}
    sums = []
    for file in sorted(assets.iterdir()):
        if not file.is_file() or file.name in ("latest.json", "SHA256SUMS"):
            continue
        size = file.stat().st_size
        if not 0 < size <= MAX_ASSET_SIZE:
            raise SystemExit(f"{file.name}: size outside the supported bounds")
        with file.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        sums.append(f"{digest}  {file.name}")
        for platform, suffix in UPDATER_ASSET.items():
            if file.name == f"Zalohuj-{file_version}-{platform}{suffix}":
                platforms[platform] = {
                    "url": f"{RELEASE_URL}/v{version}/{file.name}",
                    "sha256": digest,
                    "size": size,
                    "signature": key.sign(payload(version, platform, digest, size)).hex(),
                }
    if not platforms:
        raise SystemExit("no updater asset found")

    manifest = {"version": version, "platforms": platforms}
    out.mkdir(parents=True, exist_ok=True)
    (out / "latest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"signed {version}: {', '.join(sorted(platforms))}")


if __name__ == "__main__":
    main()
