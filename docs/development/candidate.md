# Tested documentation candidate

The learning paths were tested on macOS arm64 with Python 3.13.12 and uv 0.10.10.
The direct wheel and the wheel rebuilt independently from its source archive
have the same SHA-256:

```text
2a8f722d4ee1fef93b8bccc557ef292b2765bcef7c3b936bb0c9ec9c2d307ea9
```

The artifact is `get_nick_done-0.1.0-py3-none-any.whl`. Its uncompressed payload
is 5,691,929 bytes. Each origin was installed in a fresh environment outside the
repository and ran the documented dispatch, release, BookRec, expense and API
examples. The source archive's SHA-256 is:

```text
5f78f68e1443c6de5d1d6dd4eb9100c55fe2b1e7ba32bb097222cbdabb9f5ad1
```

These identities bind the tested package, including the supplied synthetic
resources. A CI preview also carries `SOURCE_COMMIT`, identifying its documentation
source revision. [Build your own candidate](documentation.md) when either source
changes; a matching version number alone does not identify tested bytes.

This is focused documentation and application validation. Final candidate
sign-off and publication remain separate release steps. The
[support table](../support.md) distinguishes measured profiles from metadata
compatibility and optional native/provider workflows.
