"""Worked example: Gaussian-integer RSA (see gint.crypto).

Run with:

    python examples/gaussian_rsa_example.py
"""

from gint import Zi
from gint.crypto import (
    decrypt_block,
    decrypt_text,
    encrypt_block,
    encrypt_text,
    generate_keypair,
)


def main():
    # --- 1. Key generation -------------------------------------------
    # bits=512 -> two 512-bit inert primes p, q -> a 1024-bit modulus n.
    # (Use a larger `bits` for anything beyond a demo; see the module
    # docstring in gint/crypto.py for the security caveats.)
    public_key, private_key = generate_keypair(bits=512)

    print("Public key:")
    print(f"  n = {public_key.n}")
    print(f"  e = {public_key.e}")
    print("Private key (kept secret):")
    print(f"  p = {private_key.p}")
    print(f"  q = {private_key.q}")
    print(f"  d = {private_key.d}")
    print()

    # --- 2. A single Gaussian-integer block ---------------------------
    # Every block is one Zi -- a message can encode two integers at once,
    # one in the real component and one in the imaginary component.
    message_block = Zi(123456789, 987654321)
    ciphertext_block = encrypt_block(message_block, public_key)
    recovered_block = decrypt_block(ciphertext_block, private_key)

    print("Single-block round trip:")
    print(f"  message    = {message_block}")
    print(f"  ciphertext = {ciphertext_block}")
    print(f"  recovered  = {recovered_block}")
    assert recovered_block == message_block
    print("  (recovered == message)")
    print()

    # --- 3. Encrypting text --------------------------------------------
    # encrypt_text/decrypt_text handle the byte-level packing (padding,
    # chunking into Zi blocks, and unpacking) automatically.
    message = "Gaussian primes are prime, doubly."
    ciphertext = encrypt_text(message, public_key)
    plaintext = decrypt_text(ciphertext, private_key)

    print("Text round trip:")
    print(f"  message    = {message!r}")
    print(f"  ciphertext = {len(ciphertext.blocks)} Zi block(s), "
          f"first = {ciphertext.blocks[0]}")
    print(f"  recovered  = {plaintext!r}")
    assert plaintext == message
    print("  (recovered == message)")


if __name__ == "__main__":
    main()
