"""Exact packaged command/help controls; document operands never execute."""
from __future__ import annotations

import re

import pytest
from test_public_packaged_invocation_guards import EXECUTABLE_SNIPPETS, Snippet, _help

#: An option as `--help` prints it. A whole-token match: issue 319 found that a substring test
#: accepted `--fam` because the help text contains `--families`.
HELP_OPTION = re.compile(r'(?<![\w-])--[A-Za-z0-9][\w-]*')


def _unknown_options(snippet: Snippet, help_text: str) -> list[str]:
    options = set(HELP_OPTION.findall(help_text))
    return [option for option in snippet.long_options if option not in options]


@pytest.mark.parametrize('snippet', EXECUTABLE_SNIPPETS, ids=[s.ident for s in EXECUTABLE_SNIPPETS])
def test_every_documented_command_resolves_to_a_real_subcommand(snippet: Snippet) -> None:
    """T-04-13-03. The command a reader would copy must exist in the CLI.

    Exercised through `--help` and nothing else — no operand from the document
    reaches the process, so `gnd review panel` (which spawns four reviewer CLIs)
    and `gnd exp run` (which spawns a session agent) are as safe to check as
    `gnd validate`.
    """
    code, out, err = _help(snippet.subcommand_path)
    assert code == 0, f"{snippet.ident} documents `{snippet.command}`, but `gnd {' '.join(snippet.subcommand_path)} --help` exited {code}. The packaged skill instructs a command this CLI does not have; a reader following it gets a usage error.\nstdout:\n{out}\nstderr:\n{err}"


@pytest.mark.parametrize('snippet', EXECUTABLE_SNIPPETS, ids=[s.ident for s in EXECUTABLE_SNIPPETS])
def test_every_documented_option_exists_on_the_subcommand_it_is_used_with(snippet: Snippet) -> None:
    """The half that catches a real typo.

    A subcommand that exists says nothing about the flags a snippet hands it.
    `--reviewer-timout` reads perfectly, resolves to a live subcommand, and fails
    for every user who copies it.
    """
    code, out, _ = _help(snippet.subcommand_path)
    assert code == 0, 'see the sibling test, which reports the resolution failure'
    unknown = _unknown_options(snippet, out)
    assert not unknown, f"{snippet.ident} documents `{snippet.command}`, which uses option(s) {unknown} that `gnd {' '.join(snippet.subcommand_path)} --help` does not list. Repair the skill to match the CLI, or the CLI to match the skill — but not this test.\nhelp:\n{out}"


@pytest.mark.parametrize('option', ['--fam', '--famil', '--out-', '--dry'])
def test_issue_319_an_abbreviated_option_is_not_a_documented_one(option: str) -> None:
    """Issue 319: argparse would accept some abbreviations, but a skill documents the full name."""
    snippet = Snippet(rel='x/SKILL.md', line=1, command=f'gnd discover m p {option} x', skill='x',
                      tokens=('gnd', 'discover', 'm', 'p', option, 'x'))
    help_text = 'usage: gnd discover [--families FAMILIES] [--out-dir OUT] [--dry-run]\n'
    assert _unknown_options(snippet, help_text) == [option]
    full = Snippet(rel='x/SKILL.md', line=1, command='gnd discover m p --families x', skill='x',
                   tokens=('gnd', 'discover', 'm', 'p', '--families', 'x'))
    assert _unknown_options(full, help_text) == []
