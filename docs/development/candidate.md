# Tested documentation candidate

The learning paths were tested on macOS arm64 with Python 3.13.12 and uv 0.10.10.
The direct wheel and the wheel rebuilt independently from its source archive
have the same SHA-256:

```text
812bd814329321ec3d2e6573e9a7191d59bd29f38a4f5ee4fea70f519893cd1c
```

The artifact is `get_nick_done-0.1.0-py3-none-any.whl`. Its uncompressed payload
is 6,116,293 bytes. Each origin was installed in a fresh environment outside the
repository and ran the documented dispatch, release, BookRec, expense and API
examples: 122 offline blocks per origin, including external-runtime preparation
and supplied checkpoints. The source archive's SHA-256 is:

```text
0914a1a1741577524d97974ba21a5bbd4b99cf1748505c6feb7acc7bf9adc1a8
```

The native learning paths were also executed with local PyRel 1.30.1 on DuckDB
1.5.5 in a separate locked environment, Soufflé 2.5 (64-bit), and Lean 4.34.0.
Native results and GND verdicts remain separate evidence; the generated Lean
bundle retains its unproved metadata.

These identities bind the tested package, including the supplied synthetic
resources. A CI preview also carries `SOURCE_COMMIT`, identifying its documentation
source revision. [Build your own candidate](documentation.md) when either source
changes; a matching version number alone does not identify tested bytes.

This is focused documentation and application validation. Final candidate
sign-off and publication remain separate release steps. The
[support table](../support.md) distinguishes measured profiles from metadata
compatibility and optional native/provider workflows.
