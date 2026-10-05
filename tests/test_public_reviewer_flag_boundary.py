from __future__ import annotations

from gnd.review import adapters as review_adapters


def test_flag_match_is_word_bounded() -> None:
    assert review_adapters._help_documents_flag("options: --prompt <value>", "--prompt")
    assert not review_adapters._help_documents_flag("options: --prompt-file <path>", "--prompt")
    assert not review_adapters._help_documents_flag("options: --old-prompt <value>", "--prompt")
