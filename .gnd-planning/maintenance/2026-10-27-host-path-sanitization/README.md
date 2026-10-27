# Host path sanitization, 2026-10-27

The induced-knowledge milestone close found the owner's local username inside
absolute scratch, checkout and temporary paths in retained review notes and
evidence. Record `induced-knowledge/011-owner-decisions-close.md` (CD1) sanitized
that milestone's seven files and carried the 65 files of five earlier milestones
as a separate task. This record is that task. A search for a truncated form of
the username found one more file, `pyrel-applications/evidence/PA5/receipt-path-red.txt`,
so 66 files change.

The owner approved the file list and these replacements on 2026-10-27:

| Before | After |
|---|---|
| The checkout root under the user's home (`/Users/<user>/github-repos/gnd-public`, with any `.claude/worktrees/<name>` suffix) | `<repo>` |
| A session scratch root (`/private/tmp/claude-501/-Users-<user>-.../<session>/scratchpad`) | `<scratch>`; a `file://` prefix is kept |
| The macOS temporary root (`/private/var/folders/<a>/<b>/T`), and `pytest-of-<user>` under it or under the earlier `<temporary-root>` placeholder | `<tmp>`; the `pytest-NNNN` component is kept |
| A truncated temporary fragment that ends in `/T/pytest-of-<user>` | `...<tmp>` |
| Any other path under the user's home (skill folders, the uv Python install), and truncated `/Users/<user>...` forms | `<home>` |
| The username quoted in `pyrel-agent-loop/notes/close-reading-three.md` | `<user>` |

The `<home>` and `<user>` rows go beyond CD1, which needed only `<repo>`,
`<scratch>` and `<tmp>`. Nothing else in these files changes. The 13 JSON
files stay valid JSON, and their recorded digests (`page_sha256`, `code_sha256`,
`stdout_sha256`, `stderr_sha256`) describe other bytes and are unchanged.

## Binding records are not edited

Many of these files are bound by SHA-256 in their milestone's phase and close
records. Those records are not edited. Their digests describe the bytes they
were written against, and the table below links those bytes to the sanitized
bytes. The original bytes stay in `main`'s history, because rewriting it would
need a forbidden force-push to `main`.

## Sanitized bytes

| File (under `.gnd-planning/milestones/`) | SHA-256 before | SHA-256 after |
|---|---|---|
| `analytics-m3-repairs/evidence/phase-6-red.txt` | `c2b3f234ca3500c81d31b6c8906a93a3552ce97b64d0f20ebc4e3822c4bbcd88` | `f0fa514eac27815ff0dca63cb8a16d8bfe3af6e103ee7a2abeb86706d09679f7` |
| `code-refactoring/evidence/RF2-G1.txt` | `c169a487e99d275f530a70f7d6452eb30323e36cc0e0cfaf78ef13d1b300dce9` | `67075e2cd4c6dde766c529f5b71e2671eb000224f44a6b7bdc3429c1f040cdf1` |
| `code-refactoring/evidence/RF2-baseline-pins.txt` | `838b05eb4aca2e2fde12868ce611a24515821fbcaf08eaa30be93bb00a301e35` | `a18f722b486b4517e110bc70373670faaad0bac0a2b510439f145224ac6b99a8` |
| `code-refactoring/evidence/RF2-review-capture-input-pre-fix.txt` | `a2550e4b9dcdc4eab4bb81480902160c7418e0993b01cce98897a7fa01a09143` | `b50e03fae8d6a5354f11e4836d7192545761b3bf5b9b15c57863a91d90e25568` |
| `code-refactoring/evidence/RF2-review-cli-pre-fix.txt` | `cdb48789d5031750557b0310a5408cf46d2983b9ba000acecfb5e8373d0eb5d2` | `caeb529847d36b2033d74724c26404a825dd788b886e24d41c8f3a687d6d5b64` |
| `code-refactoring/evidence/RF2-review-pre-fix.txt` | `1e4dc49893f596de0b0ed7509872e6c612cfc2361b4455f9daaf7fee00e74ce2` | `1e1f1784812e35c29aef333f976154a894f121a9531bc0520d9fe36606e32dd7` |
| `code-refactoring/evidence/RF2-successor-interpreter-pre-fix.txt` | `e3c23492ebd7decba6956d01eb03557f3f6c936469261c4115f9bfa95d152f37` | `74629c96f672d7702f4fc8a8cdad700645b3094ff665bee1022834d1c4d5d916` |
| `code-refactoring/evidence/RF3/moved.txt` | `73cacf7f8197d5b6ff8a7c5bc248ebcb085e6a99a380e980869b3e00e6bed593` | `45b7ad750ec0e07160ea5ff9909a31746308d3f0f2d91407f604418997553db9` |
| `code-refactoring/evidence/RF4/cache-stimuli-pre-fix.txt` | `7fdc43ab76ef0062fbb2286551612a091356e46896382bf0997af2153c963219` | `a4060cc7752f0d10972c408c624e32a50230a9fd987d00f12a52b45b0c2af2f2` |
| `code-refactoring/evidence/RF4/move-fast.txt` | `148665dd76a2700418e50b6798a051d17e11b6b3c0fe6e4fb6444391a0962a67` | `36e1b39434be6a696446950a99301445a5d25b2cda3a2ae08e06835c2bf605d7` |
| `code-refactoring/evidence/RF4/moved-G1-final.txt` | `f9b603dc7723cc761c8ebe38966febfaf6f72e199cd7ad976dc9011f35a41bef` | `56af2a1e330022d461877e077d483a5787222646b3848340ce9dd2aea88fe04b` |
| `code-refactoring/evidence/RF4/moved-late-impact.txt` | `281f1ce99b65c45ad50a66852df645bf61211f6d4263f44a62d0e8fb694969ac` | `de7d9989b4c09165aa4f3df2c6d9a2cec3cef1ce422b3acc8254df06fdede0a3` |
| `code-refactoring/evidence/RF4/review-guards-pre-fix.txt` | `d6564f46110b3f83af7361da707d408b607fa8e68c8ed5cb99c721d527cc0dd8` | `b3ef2296f7b0c6833b1115141b72a7ffe01bf3213802f97b434955a55c74867a` |
| `code-refactoring/evidence/RF4/review-regressions-pre-fix.txt` | `c4d973a9cf3bd2c4c596f2e968337dc12baf868a4bd3d00f6cc8fb9ae01bb2af` | `6805d1f18440c3c976807bfb7f5846f102417f44c30d07bef0639d63e53bae20` |
| `code-refactoring/evidence/RF4/routed-scaffold.txt` | `3f788001bebc8fea5179d447a4b086ccbc9043b8887c7999306cfd20ac3f1268` | `4e28e64e427f62cae14ad10665539b41260763deaf7f5053cca6db191a17379d` |
| `code-refactoring/evidence/RF4/scaffold-base-reproduction.txt` | `42246d03fee097a4eaf4551eb65ca3e5956ec6c77397cc102928778e4374ac6c` | `8f356fceb5091fe95648fa5efd4d8ab181ebc4b172390c4246529668934b28e4` |
| `code-refactoring/evidence/RF5/G4-py311.txt` | `e1e0d8a0d15e6293577a16c5e1c38ae550e0724f3b96dd04f84795e8295f6e62` | `0b6400b78b0d6890c49b8cd4531ca12a96c336021839fee1f08918cb1f6bfe64` |
| `code-refactoring/evidence/RF5/G4-py313.txt` | `79b30c75c2c5054ae30c6b2604a6027aaf10c4f277c1e091522ef30f89199300` | `a44035dadf617246e9ea461b51012c9af666adedba0376bd20a05dcce24f7ac3` |
| `code-refactoring/evidence/RF5/moved-handler-pins.txt` | `7384e0df3864347433e6953ad9e303a24482e6e87506e1d2dd1b9c1b31457fd7` | `6dd4ec9508ddb66413a6d6d8ee80c17e4ead9ec7082e05d6fe10b48775fe0210` |
| `code-refactoring/evidence/RF5/moved-impact.txt` | `123c9c2fab832fcfca1196c6638fa089510b14e926bd4307141a475462a5296f` | `d6289691ecbd401b20f5375677c4a849b001647ca78636130a1320f1e8758882` |
| `code-refactoring/evidence/RF5/predecessor-handler-pins-repaired.txt` | `d52078dbd902d59e4f0a1bcbfe67d27b4df11ec5df7129c0607398013a5e7ca8` | `219ee0668ecae5033515bc0fc91ee178f0a99d0ef98d8270fa0cb1c7540db77a` |
| `code-refactoring/evidence/RF5/predecessor-handler-pins.txt` | `3dd7a7b139aad97a5a0080ad72bec080484ab5bf98133629afb10fd068152d98` | `dce257eb62a040bfb9e09ec37de0200bddfd2e104b3de7ed157ef0a343f18dda` |
| `code-refactoring/evidence/RF5/review-regressions-pre-fix.txt` | `a6c51801b80835baad0a07345353bac47e46c930ef0ecd2dbb08aac7ab3e66f7` | `33dfc17f96bdd4e41cf339a7b2308239ca0419fa44b53b6c3af0867f7df6d1db` |
| `code-refactoring/evidence/RF7/current-rf1-repair.txt` | `dd2ed2a05f46e1fd2e0b85ff1c898b98a56a841238865cb1be0157d5db7869aa` | `4132656a8a94eee76c24537825aab561ce91b94d0917755e9ca503f1263f98ef` |
| `code-refactoring/evidence/RF7/current-rf1.txt` | `8a17a85a4395d75f5140029de100067beb6f30b88ad260d4af61cc709f4285a0` | `72b9370c793f8f68db9123355075aa58bd34768a1d334cfb20e19e296cf50231` |
| `code-refactoring/evidence/RF7/restriction-red.txt` | `95bba748f9726bdf7af9f3ddbd0d8ab1727f76517839a879fcbd36a99284c1ca` | `e0fe60938bd5c32d45c2837c95ce8b7259ca8199fa6b98a43b78785a1d3ac5f4` |
| `code-refactoring/evidence/RF8/empty-reconstruction-red.txt` | `67f62d1c95908fa64f833b9a9fd05be48fb92eb40dc71054a5b5e1517b089274` | `9de9c90f3e15b0bacb63a3c97b3190a78f75f193c6606040fd16bf869685d03e` |
| `code-refactoring/evidence/phase-RF0/review-regressions-red.txt` | `c72e95bd8f23916e5f4ad4be4cd4b757f338cf3ad4190ceff9798de964d55c49` | `413034b9c95aa48811931360ce897f30b2911a766b47292ebecdf4f7a0fc4c43` |
| `compiled-snapshot-obligations/notes/ci-assurance-review-two.md` | `8c402d1819e906cbcf637c5a7b6fe0540f3894cca39f0ece75ca0959a19e4b9b` | `8e5a6726e9d22d09b3d573fc431c7ca707c05d8dbb9d31fb9425f30eaf25d24f` |
| `pyrel-agent-loop/evidence/PL5-review/replay-red.txt` | `a9cb3f983a0d163f5c8b1138709223dbf6396e9dbfd2f3b8305ef27a76097f5b` | `39fec603536c068cb32a73884326d351f01a18806e8d8a567863b3c70e9a33fb` |
| `pyrel-agent-loop/evidence/PL5-review/review-boundaries-red.txt` | `3987ab426d584a6a3a05f4b68dd5920933a080e35bacd543c4ab0a87c1993f41` | `e01d051c71956200050d0d9f775efffed0f47a8458dfeee8932002e0c6aa84ca` |
| `pyrel-agent-loop/evidence/PL5-review/review-helper-red.txt` | `3747fd0262281b0a5cb7cc3bce6390272c59122cbe21fa2ea0d4779f8426f862` | `73f5bfae98ec508054edfee7c3def4d6961842f1d3c6312502c97fb7ee6d3fb0` |
| `pyrel-agent-loop/evidence/PL5-review/review-red.txt` | `ee57840ab6f6f928850fa690075625dde4bc3ba785ad031533dca80061fbee2e` | `ab4476e98a29e4a9c8434f83aab0978263f3797df2d9f4bf7f8c2f60b848c9b0` |
| `pyrel-agent-loop/evidence/PL5/resume-excerpts-red.txt` | `2fa41ddb996d772bf9cd1fbde283ceec964e6a42879dde85e10b2ba1cddb568c` | `9c4216afca4bb14984c1886775cd5ec91e65cd1441f8dc0a80d3f8bc1c7db70c` |
| `pyrel-agent-loop/notes/close-reading-three.md` | `4755de5e0645bbcb07f670dd33afe3be766dded86e61d8a66eecb38bb9c7164d` | `a77997d60e282bd4cc7b94d81b079dcbad9a73eb26d377c303c61c0a799ad34c` |
| `pyrel-agent-loop/notes/phase-PL12-claude-review.md` | `06837aa1cbebe01860734939115901bcc76ac352f94b136165a7b344b97c11f3` | `b1c2b4335f1f4c1c602a427002a5e72d833bf8549eeaea8868d8f648d0a2e2af` |
| `pyrel-agent-loop/notes/phase-PL13a-claude-review.md` | `a32a1459835d205db4cdb6daa41f065de71d299533a6c4abf07f971dda4980e0` | `6f69ae376b9d541a86e5c5c2164209bb280b814ca9c6b9367c9b9e4bd61b3989` |
| `pyrel-agent-loop/notes/phase-PL13b-claude-review.md` | `aa088b0e2032c5923f776da825fa77bcdcf8961de789428f6d3c41037c05b668` | `7944f94cf5ddfa24d2e09eab8f766f55d55f6aaacb7bb8d600d1ff2ae68e9552` |
| `pyrel-agent-loop/notes/phase-PL14-claude-review.md` | `1472270641fd1781ea2c9b902e398ca5d834480abcbd655195d5a2851781c574` | `9b29fe76542aa72042322d09245aed9ee4e773113c693cec0a9f0185382d20c3` |
| `pyrel-agent-loop/notes/phase-PL16-claude-review.md` | `54e286287eb271171790842bd38214225ac905ff3a70438f1daf1446f5a6f47a` | `93c34d6f0d730407c4842f34faf94a106cafe1565e2d8b8b0ca05e6138198d32` |
| `pyrel-agent-loop/notes/phase-PL18-claude-review.md` | `16bec3ed999e3f306024d29ee831e92f2b150591f649306ad9d9f18305dd7fd1` | `86ee5c53942a4e1fac3f0a54978f37bbe7ce47f3d5766ba8ed9f498565ca8445` |
| `pyrel-agent-loop/notes/phase-PL2-claude-review.md` | `4dbbfa23f0c3aca75ac0e17f8834bc1ee42a59817a80ec789c6212ead782224d` | `af86b1ba456a334332a24121e3555cf11da1792da1f35e9ffe452a428166af64` |
| `pyrel-applications/evidence/PA1/review-parent-expanded-red.txt` | `fd07332bf59dd4668ed7cd281337fbb130e16af48898827029f2886e37d0eb35` | `6ad4e921589621f23329188cf66fec811baa1f1bfe4a85a53cde1897ba1c2c4c` |
| `pyrel-applications/evidence/PA1/review-parent-red.txt` | `babd111b60c83a2c137e6120a34e5d39fe3647382430e6e38ec4fd9424f111b6` | `cbef7f28d74f6e40d677284988c8d8f1c2fa1a25f639d90eb0b1b78a0290d2b0` |
| `pyrel-applications/evidence/PA3/native-interface-red.txt` | `ab01f3dea5ab663b78f5911510586f4573ec2d972f69f52ba10764822bc0ad31` | `d722430b6d84434ae0c9233d582dc5f016b822768c260db6428b79909ee16126` |
| `pyrel-applications/evidence/PA3/native-red.txt` | `44d8898d9a2b8354c3edf811bb3cea68feb24bb381700c5be1a091cf60239fb4` | `b85c1cb5364c8f6634f0e54c3e0ed1d0dba2e3511e9e7686c635f8616aae7354` |
| `pyrel-applications/evidence/PA5/receipt-path-red.txt` | `ec0ceceeaeca8710b2038db65a31b6321f3fb86fd38d00863a7a7c74f45549f6` | `56dec6c7a6673b48c8c18a895a6d9b27e412f31fa3f516324f8e9817b899ca6d` |
| `pyrel-applications/evidence/PA5R/bookrec-offline-closing-steps.json` | `7863986ed834237acfb7f6966706268b8009d2dc6cea432c67ac3544a90788f2` | `926ebe9546a32f379704a19dee6bb0ef4bf94f4dd1f66b88b209b039a4abec3f` |
| `pyrel-applications/evidence/PA5R/bookrec-offline-final-steps.json` | `feb74bd455e4149665e786aa23209ad2611662eb3d1dc575b6ab070035d63818` | `a6fe5a61b9ae039649d43027c6d28daa5dbaab455286bd2c86c8834ed753ec42` |
| `pyrel-applications/evidence/PA5R/bookrec-offline-steps.json` | `e46032399c2afcb4fad85338027ccd0886764bd0f5dd9a7dd041605cadf75d6e` | `363a2452db06971c08e957e92da4fbefc61fe759a31d9b193cd897eab9b46553` |
| `pyrel-applications/evidence/PA5R/bookrec-pyrel-closing-steps.json` | `b2ff0122bb214870ba1404cc1e9b37076e25eaf0206dfc15af341eb4611cca78` | `6d661da15224c425e4edd5a090ffee4077d1fbc67ecd1a4ebd6017e6f1355f6f` |
| `pyrel-applications/evidence/PA5R/bookrec-pyrel-final-steps.json` | `1c42024b2fa867eca9b990d75c31531c3b3887c8f1ae207b260ad782089c9b00` | `71e8843f119bd3e0f8511602778ac2ce497194ec4c60928d7c9f6dc106e7c04c` |
| `pyrel-applications/evidence/PA5R/bookrec-pyrel-steps.json` | `1cf194ea2be426571d63e92911b74f094e6f2676d93dd1ead572b2e456ddc13b` | `2a03812855587c800c59bd96da734cc98f6e17a43581ed15ddea386e10fcd0e5` |
| `pyrel-applications/evidence/PA5R/expense-offline-closing-steps.json` | `dfe1f666d08f28ae36e7b6251a24ca361c2c7628e249b5693be8d6056a5df38c` | `83083feac1011a81a9482a1bf22c10ef5d5f32a7e4aa2b403e600c8a1237df61` |
| `pyrel-applications/evidence/PA5R/expense-offline-final-steps.json` | `b6ce365986cef316b6121654e2906a7349bb2f8b248329acc5a7958f4a7011d7` | `9df83b0b870ff8b5c08cd953695485ad4f43e6520bc7fbaafab101d05bb8d725` |
| `pyrel-applications/evidence/PA5R/expense-offline-steps.json` | `8b5c0617bfdd612f8c9e8cb8304c03c7427c0d3db74a2471b441be2f54362ca0` | `66abd8adfc22acf03d5204891b286fd667343e327bd1c5b52d378b7f7d5b357a` |
| `pyrel-applications/evidence/PA5R/expense-pyrel-closing-steps.json` | `decd3afb7b499607cf197d1c877f855c95d4f16238154ed851c1db374edcacc1` | `7ae88424412024c3f97dd3f87cfcebf8e2e095153ecb6517d75221ca0346f7e3` |
| `pyrel-applications/evidence/PA5R/expense-pyrel-final-steps.json` | `b5138befd93be2627f2ab89494757d1c07666bbb3dfa7ff830111299c3e7d54b` | `01ca0151d1ce0c44ae319b6505907f51f0101393f7e7c7ebe342c0ff80d9a2cb` |
| `pyrel-applications/evidence/PA5R/expense-pyrel-steps.json` | `a10c7b51095ae75c42893373babe5f25e6e60c5a108c7c13f0a40ba09b84b9e7` | `f6c18829e6f1062293fb4dfd5e644ff1d4c2ca0524133a3064a41ee7b8dee11c` |
| `pyrel-applications/evidence/PA5R/focused-default-final.txt` | `24fe7e2509e361700cd912ebb3c762b05060687e975b6fece451fa9c0e03b34a` | `fc8ad21ee5617023910ee477fa5b0436ab37f9f79394c47794feeef87588d39f` |
| `pyrel-applications/evidence/PA5R/local-ci-50eba83.log` | `03132ae105dee348fc9cbafea6f2c0efda0c3e18b400e043bc74f1e609da1353` | `79202fdffd9ae403d110101533bfc1300a82bceb38ff30a220440f15ccd72b38` |
| `pyrel-applications/evidence/PA6/e-receipt.json` | `bd5da83348765fafc1741dc8eea8f112b519cf4d0183f827dbfcd1325f0894d3` | `e2ddde494ec21c56991cc875276b39c635a1e2de30567a394a873f6925ee263c` |
| `pyrel-applications/evidence/PA6/install-red.txt` | `8a34abe9ecb37f1a870dfd2cc900399e84413d8c29dcf4a86a5e9cd12a4cbd29` | `feb1cd2e8e27307a806e4c6722eab854e8f25eb81d2a87b33dabd3e2aa557e5b` |
| `pyrel-applications/evidence/close/local-ci-d3bad6e.log` | `c5c425d5a661d6b17bf1d9a9259c42b3648c86bbc9cfb8774d3313daa64d2433` | `6fdac92bda3c4fb724afd9ff4bf9d474a28da9b6ffd3a3202aadbe27d0bb0ccb` |
| `pyrel-applications/evidence/close/setup-verbatim.log` | `0b6874a9b41767be940d0881518edc8f5c8ab6360235b50db8ce0818138ea994` | `e6fca0f3aba98dbdd549337f98b80ce5734d46990d3cede54e59d0f729eb76ff` |
| `pyrel-applications/evidence/close/setup-verbatim.sh` | `b06b05eea6cd71eb5437755aaafa3e027b82b84e8638c6a8210d379ced43bf9f` | `a9a039a90d520bc29bf82907440cefda19b7b3fd088cc9c49edc1f956e48e856` |

## Verification

- `git grep` for the username, and for its first nine characters, finds no
  tracked file after this change. Only `main`'s history keeps it.
- No test pins these bytes. The 46 test files that read `.gnd-planning` or name
  a changed file were run on the sanitized tree: 2629 passed, 78 deselected.
