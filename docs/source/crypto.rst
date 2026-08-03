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

Further Reading
----------------

Foundational paper
~~~~~~~~~~~~~~~~~~~

- Elkamchouchi, H., Elshenawy, K., Shaban, H. (2002). *Extended RSA
  Cryptosystem and Digital Signature Schemes in the Domain of Gaussian
  Integers.* Proceedings of the 8th International Conference on
  Communication Systems (ICCS 2002), Vol. 1, pp. 91-95, IEEE. The paper
  that introduced this scheme: modulus N = P*Q for Gaussian primes P, Q
  with \|P\|=p, \|Q\|=q ordinary primes, key equation
  ed = 1 (mod (p^2-1)(q^2-1)).
  `IEEE Xplore <https://ieeexplore.ieee.org/abstract/document/1182444/>`__ --
  `Semantic Scholar <https://www.semanticscholar.org/paper/89eb12ee80c1e160a3596831f0efbfe84192a214>`__

Extensions and variants
~~~~~~~~~~~~~~~~~~~~~~~~

- El-Kassar, A.N., Haraty, R., Awad, Y., Debnath, N.C. (2005). *Modified
  RSA in the Domains of Gaussian Integers and Polynomials over Finite
  Fields.* CAINE 2005, pp. 298-303.
  `Free PDF <https://www.academia.edu/12482120/Modified_RSA_in_the_domains_of_gaussian_integers_and_polynomials_over_finite_fields>`__
- Pradhan, S., Sharma, B.K. (2014). *A Modified Variant of RSA Algorithm
  for Gaussian Integers.* In SocProS 2012, Advances in Intelligent
  Systems and Computing, Springer.
  `SpringerLink <https://link.springer.com/chapter/10.1007/978-81-322-1602-5_20>`__
- Cotan, P., Teseleanu, G. generalized the key equation to
  ed - k(p^n-1)(q^n-1) = 1 over Galois fields of order n >= 1 (n=2
  recovers the Gaussian-integer case); see the partial-exposure-attacks
  paper below.

Cryptanalysis
~~~~~~~~~~~~~

Worth reading precisely *because* this module is a teaching
implementation: the scheme has been broken under the same conditions
plain RSA is (small or exposed private exponent), via continued-fraction
and lattice methods analogous to Wiener's attack on RSA.

- Nitaj, A., et al. *Cryptanalysis of RSA-type Cryptosystems Based on
  Lucas Sequences, Gaussian Integers and Elliptic Curves.*
  `Free PDF (HAL) <https://normandie-univ.hal.science/hal-02320970v1/document>`__ --
  `ScienceDirect <https://www.sciencedirect.com/science/article/abs/pii/S2214212616302678>`__
- Bunder, M., Nitaj, A., Susilo, W., Tonien, J. (2016). *A New Attack on
  Three Variants of the RSA Cryptosystem.* ACISP 2016, LNCS 9723,
  pp. 258-268, Springer.
  `SpringerLink <https://link.springer.com/chapter/10.1007/978-3-319-40367-0_16>`__
- Peng, L., Hu, L., Lu, Y., Wei, H. (2016). *An Improved Analysis on
  Three Variants of the RSA Cryptosystem.* Inscrypt 2016, LNCS 10143,
  Springer.
- More recent lattice and partial-exposure attacks on the generalized
  Cotan-Teseleanu family:
  `Partial Exposure Attacks (2025, open access) <https://www.mdpi.com/2410-387X/9/1/2>`__ --
  `A Lattice Attack <https://link.springer.com/chapter/10.1007/978-3-031-76934-4_25>`__ --
  `Further Cryptanalysis <https://link.springer.com/chapter/10.1007/978-3-031-22390-7_9>`__ --
  `Further cryptanalysis of some variants <https://link.springer.com/article/10.1007/s12190-024-02292-0>`__

Survey / background
~~~~~~~~~~~~~~~~~~~~

- Koval, A. (dissertation, NJIT). *Security Systems Based on Gaussian
  Integers.* Covers the extended RSA, ElGamal, and an extended Rabin
  cryptosystem over Z[i], with a caveat worth echoing here: the
  extension only helps if breaking plain RSA turns out to be strictly
  easier than factoring, and even then it is not guaranteed to add
  security.
  `Free PDF <https://digitalcommons.njit.edu/cgi/viewcontent.cgi?article=1332&context=dissertations>`__
