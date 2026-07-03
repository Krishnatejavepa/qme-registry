# QME signing keys

## Validation Certificate Ed25519 public key

Certificates issued by QME from 2026-07-03 carry an Ed25519 signature a
third party can verify with no secret. The published public key (raw,
32 bytes, hex):

```
01e8df96a0c3b6ecba98c24be34b0978230b924b9b9eceffd25536a712081c49
```

Canonical copy: `protocol/keys/qme_cert_ed25519.pub` in the QME workspace;
this file republishes it where certificate recipients can pin it.

## How to verify a certificate

1. Remove the `integrity` block from the certificate JSON; serialize the rest
   canonically (sorted keys, separators `,` and `:`); sha256 it. The hex
   digest must equal `integrity.content_sha256`.
2. Verify `integrity.ed25519_signature` over the ASCII bytes of that hex
   digest against the key above.
3. Check `integrity.ed25519_public_key` equals the key above. A certificate
   signed under any other key was not issued by QME, whatever its signature
   claims.

With the QME CLI (from the private workspace) this is one command:

```
QME_CERT_ED25519_PUB=01e8df96a0c3b6ecba98c24be34b0978230b924b9b9eceffd25536a712081c49 \
  qme certificate --verify <certificate.json>
```

Or standalone, with `pip install cryptography`:

```python
import hashlib, json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

PUB = "01e8df96a0c3b6ecba98c24be34b0978230b924b9b9eceffd25536a712081c49"
cert = json.load(open("certificate.json"))
integ = cert.pop("integrity")
body = json.dumps(cert, sort_keys=True, separators=(",", ":")).encode()
digest = hashlib.sha256(body).hexdigest()
assert digest == integ["content_sha256"], "body tampered"
assert integ["ed25519_public_key"] == PUB, "not QME's key"
Ed25519PublicKey.from_public_bytes(bytes.fromhex(PUB)).verify(
    bytes.fromhex(integ["ed25519_signature"]), digest.encode())
print("certificate verified: issued by QME, body intact")
```

Signature verification proves issuance and integrity. It does not prove the
verdict is right; regeneration does that (`bash scripts/verify.sh`), and the
two checks are independent on purpose.

## Key hygiene, stated plainly

The private key lives on one machine, outside every repository, and is never
in CI. If it is ever rotated or revoked, this file changes in a signed-off
commit that names the reason, and previously issued certificates are
re-issued (superseded, never edited) under the new key.
