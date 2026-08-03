Crypto -- Gaussian-Integer RSA
================================

An RSA analog over :class:`~gint.zi.Zi`, using two inert Gaussian primes
(rational primes :math:`p \equiv 3 \pmod 4`) in place of RSA's two rational
primes. Each block carries two independent components (real and
imaginary), so throughput roughly doubles versus plain RSA at the same
key size. See the module docstring below for the underlying math.

.. warning::
   Teaching implementation only -- no OAEP-style padding, not
   side-channel hardened. Do not use to protect real secrets.

.. code-block:: python

    from gint.crypto import generate_keypair, encrypt_text, decrypt_text

    public_key, private_key = generate_keypair(bits=512)
    ciphertext = encrypt_text("Gaussian primes are neat.", public_key)
    decrypt_text(ciphertext, private_key)   # 'Gaussian primes are neat.'

.. automodule:: gint.crypto
   :members:
   :undoc-members:
   :show-inheritance:
