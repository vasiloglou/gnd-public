# Compatibility and version policy

Distribution `get-nick-done`, import and CLI `gnd` remain stable. Versions 0.1.0
and 0.2.0 are published (0.2.0 on 2026-11-08). Version 0.3.0 is prepared and
not published; on 2026-11-11 the package index listed only 0.1.0 and 0.2.0, so
0.3.0 was free. Confirm service ownership and that the version is still free
before candidate freeze and again before any upload. Milestone numbers are not package versions.

Preserve documented schemas, exit bands and deterministic behavior unless an
explicit reviewed compatibility decision says otherwise. Record breaking changes
and migration instructions in release notes. Do not overwrite released files;
corrections receive new version/artifact identities. Base dependencies remain
separate from optional synth/provider/native requirements. Python >=3.11 metadata
does not assert every interpreter/platform has been tested.
