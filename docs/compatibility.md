# Compatibility and version policy

Distribution `get-nick-done`, import and CLI `gnd` remain stable. Current 0.1.0
metadata is provisional; confirm service ownership and an available version
before candidate freeze. Milestone numbers are not package versions.

Preserve documented schemas, exit bands and deterministic behavior unless an
explicit reviewed compatibility decision says otherwise. Record breaking changes
and migration instructions in release notes. Do not overwrite released files;
corrections receive new version/artifact identities. Base dependencies remain
separate from optional synth/provider/native requirements. Python >=3.11 metadata
does not assert every interpreter/platform has been tested.
