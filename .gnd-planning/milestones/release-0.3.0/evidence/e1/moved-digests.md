# Moved digests of the RN1 M5 edit (measured in a scratch copy, 2026-11-11)

Produced by applying [rerecord.py](../RN1/rerecord.py) to a scratch copy of
main `d7317d25` with M1 to M3 applied (never to this repository), then listing
every changed file. Old values are from `d7317d25`; new values are what the
commands print at 0.3.0. 30 files change, 445 insertions and 445
deletions; the binary patch of the edit has sha256 `c3f61b02fd04cfbbc1b3abcc3378983b61ab259a6a8c1ffca517b5fa499ba3ff` and is not
retained (the script reproduces it).

What changes inside each file is the version value 0.2.0 becoming 0.3.0, a
digest or member digest that follows from it, or, in
`tests/fixtures/rf2-pins/measure-successor.json`, one sentence appended to
`reason`. This was checked twice: by the script, which refuses to write a file
whose old and new bytes differ once version values and 64-hex digests are
masked; and separately in this session, by diffing every leaf of each gzip
payload (equal payload lengths, equal key sets, changed leaves are member
bodies equal under the mask or member `sha256` fields) and every changed text
line.

The seven gzip containers are written as `gzip.compress(payload,
compresslevel=9, mtime=0)` over compact JSON; that recipe reproduces each
existing container byte for byte from its own payload. In a `.py` row the only
change is the pinned container, payload or manifest digest literal.

| File | Old sha256 | New sha256 |
|---|---|---|
| `tests/fixtures/induced_knowledge/ik1-baseline.json` | `354439260fbe4dfe7eaa533215e73b3f71b9b38eff87e494fd04d87540107d23` | `d52cd4a72624f434f1b2d484af036c5dea21f4cd33a63edee02f6d1e033445b6` |
| `tests/fixtures/induced_knowledge/ik6-walk/goldens.json` | `74cd10ccd0a3064442158a8fbfbb4d20a98d5c873575ea188ba33c3ee95dfb12` | `404b8c09e4839dfb82ab088ceb171038e10506a1f34a7428412b57ac525b399a` |
| `tests/fixtures/public-book-runtime/workspace.json.gz` | `38d5da120cb87529a766534c08db2a2251eae999c6982c325c3511d91faa3ee2` | `241f9a36e3dfa118f254a342d23e33836ee7fa51b3164bf935587670ded40f24` |
| `tests/fixtures/public-book-skills/workspace.json.gz` | `b530b9603a0f7ac3e44c18f7b9c80a0967e4b9d47a8489a9dc73decfcf3bb5a3` | `3857a66362072ddcb553a68cf9a5a1273f4a130fd6eca765095a143c46941999` |
| `tests/fixtures/public-coverage-goldens/corpus.json.gz` | `965a29cbc2dfa293608cb0a4640b8a677202fcd3aa4684eab641ab472521fbde` | `2617ce2127b763e63b11dcc42646cabd241375e2fdfbe22abde6dcb7514179df` |
| `tests/fixtures/public-expense-current/workspace.json.gz` | `33bcf3ed3f570547bf1af9e90c4a765aa36be28528262663f74a0b2d623a4498` | `3e1357009928fd66c3a06f247a156319badacda62b4413f6a4c5cdcb4a0684ab` |
| `tests/fixtures/public-extract-controls/workspace.json.gz` | `9e9f3c1688060253297b4627585cf23da801304eb0ab06b484485d70e85a178c` | `10d1d72476e9df41212a0093c7515ab391d2ab95f54101f79346f7ebcf67a430` |
| `tests/fixtures/public-launch-phase-3/measurement/measurements/movie.faker.json` | `340a9d5de570e45db6e30b1974fdd511555d8dd5c0d799beed5a11a582e1cd05` | `d310f2f5455235e88ea728cf70991c176e0c0e518472000f6b2ed05712709fac` |
| `tests/fixtures/public-launch-phase-3/measurement/measurements/movie.llm-proposed.json` | `6042b78a10cc49f602a652ecc7e73043a433826042a45b46c95840d1d7f20c57` | `6a9caf3a07e439381ad0180f3042edc8677790966a29301d5208ef61a10ca912` |
| `tests/fixtures/public-legacy-codegen/closure.json.gz` | `468390e58a3476e3e1c39b3d9564a6517320a9bd5f38dec01eafabe8aa97e75d` | `3070a95babc6641bd33b99036b7eaf0e725d77c64f21232d3eaacc688f0b49b6` |
| `tests/fixtures/public-measure-corpus/workspace.json.gz` | `71df5a418f39ef86f142ebfd4c2f85a5b8224ab2f6ed6935e3663b46838500b4` | `49a384ddd0825db4e77db8eed2bc08cc1dc4fcf84522bc9e26310125bc4840d5` |
| `tests/fixtures/rf1-pins/goldens.sha256` | `118e80d4de443d71561bbad95a7294cd96c9ad8697f6dcf348f6e08fcaaf9ae2` | `839d7d9d8e6db9aca815e90efbc033ee9a57ffc1c67e4e9df795d2a3a5aa44be` |
| `tests/fixtures/rf1-pins/goldens/sem-synth/ex_approvals_model.orm.yaml.json` | `35079aea3bd6006ef82ee459ae8631ce45ced611f832de00f2cd50d1426280a9` | `44c2436edc748b5d37f673ee2b1291e30dabc6798eb0e24bd92c63408649d124` |
| `tests/fixtures/rf1-pins/goldens/sem-synth/fx_checker_ring.orm.yaml.json` | `1ecefe496e2447eaf26dc89bdfa9bb86d60e5c1f37b364af9fe0270fa0e12f84` | `58b9c77a38ffc70516060dde2300dad440d8345f084c144c1d85bc570f0365fc` |
| `tests/fixtures/rf1-pins/goldens/sem-synth/fx_checker_setfam.orm.yaml.json` | `4b05f9b71b52376b60d6735c7f970022cbbb270590c852e2033ae8c3b5d8df9c` | `470f870abf23be3eac36bdec390a92920a3196c6fc8b2f205f981c9658b15c05` |
| `tests/fixtures/rf1-pins/goldens/sem-synth/fx_models_dispatch.orm.yaml.json` | `2068b0f480fe23f5d6a92730a819ef424d0965a7de14bad4e098acaa0fc33691` | `65f51a65aaf4ce2c2e0a8b05c6d0ed01f936160578508dce180756f36a76179e` |
| `tests/fixtures/rf1-pins/goldens/sem-synth/fx_models_full_vocabulary.orm.yaml.json` | `0c168744dfd39a64668864d6faaf0e738ffe74ad8ba2df9bcc5b9bc0b68ce32d` | `cca015139089a450bd495610a3cdc65c6615dec43cde4a8ce52f5e033e6f2d73` |
| `tests/fixtures/rf1-pins/goldens/sem-synth/fx_models_keywords.orm.yaml.json` | `586b725b1848b0d2abd60cd61423ec39dad763d2d85a644143b9ffc0ad4e59a7` | `d0819f904ece2954fefd21e6aaa3205488f7b6ffabfa02bf7a46dba708a42bcd` |
| `tests/fixtures/rf1-pins/goldens/sem-synth/fx_models_v2_operations.orm.yaml.json` | `e34224661a170518e1bfcb5860bc89c3609cd752e9e109fe99086f511c5f1b01` | `3ccf1a04126198321ad6da146f23acff1683d82eceaf74827da0f65ac2b926a8` |
| `tests/fixtures/rf1-pins/goldens/sem-synth/fx_models_v2_worked_example.orm.yaml.json` | `da640a8fd14e0509e7bae58cb574d41713fa80f431ba0ce12018038e1e38e6e3` | `59b4d085c3c323d20013de62aa646c1e5348e894f3ba13812b5134cc471fd665` |
| `tests/fixtures/rf2-pins/measure-successor.json` | `110b8fe27f4ff81290eb38e9e0713798e9ae9f4c1c22774b9f464c49c4b5f224` | `ec679a11bb14a724826f90083864fcbd6b3170bb10dc786778c9c7e648aafa3c` |
| `tests/fixtures/roundtrip/artifacts/setfam.artifacts.json` | `c66bc6734dac81810dc6ffd1574eef05ce4d420ad5560e6f6589b6447625fd66` | `75006d58edbc6bf649881bb1dd92067e5412e5c4e0a91a9287ecaf11ae2ab837` |
| `tests/test_public_book_runtime.py` | `4d5586dadb71ed1b255f102ff4a43a7f1a7de9359b9ff9396c35115e1992c6b1` | `021ec01fa7fd7c45e0f58e657a16c4856302894801a015689b0f3eeb9e6ff094` |
| `tests/test_public_book_skills.py` | `74bdfae2ffb85d09723e37bbdc8dbfc117116e6183a30819108be3a2fd0194ea` | `43da3720c41efdbd3bcdf5b5c7bcb76b8b1e7e87930ace970c122e88685c4826` |
| `tests/test_public_coverage_goldens.py` | `f574b63ebbd24062f551e7ce618b4eead4700d5a43598234794daf85d6cea640` | `41bd5d66b5823520466e802274fc0926f97e496677a3bb4c9ba2821b23183f29` |
| `tests/test_public_expense_current.py` | `192907c5789cd5eefea389c87ef22bf74c6b18aec03a25f72ac7130c4bdc1965` | `ca2332cf46909136a4749d00f26fcb2bf680b1b4807ff034ca96db5aa9837925` |
| `tests/test_public_extract_controls.py` | `906f284eeca9df58be2a44b04ee9adff3830c556bf48085f01fb24b60e93a668` | `0a7490789924727c1fde8ab60346dda29f94f1d96ec9320ce3b794eb87bdca5d` |
| `tests/test_public_legacy_codegen_pins.py` | `e64ce0b729bde102e6a2f01cfe18fa7ce78253d11d889f590d1df4eb85d2da57` | `4354500f5a982ff4398223cd025669586753145a101886803008ab16809cbeaf` |
| `tests/test_public_measure_corpus.py` | `abbb32b16e97085bb188c96280de1acce7490112d5d418cd5cfa30db9a3dd51b` | `999f6d4c1d4270177eb9f306ce6914d0cdec4a968da3e5f380a65dbc0c2c7071` |
| `tests/test_rf1_pin_harness.py` | `96babaef5805cf05a788d5854bf59373c97fc31d937447b47a258d36e20487ba` | `e799320ef1f132324174af7d125ea12e80164ddae215b393ef44c633d743249a` |
