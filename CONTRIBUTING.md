# Contributing to Compowater

This repository primarily supports a specific research study. There
isn't an open call for feature contributions, but corrections,
reproducibility reports, and questions are genuinely welcome.

## Reporting a reproducibility issue
If a documented command didn't work as expected, open an issue using
the "Reproducibility issue" template, including the exact command,
the full error, and your OS/Python version (`python --version`).

## Suggesting a fix
Small, focused pull requests (one logical change each) are far easier
to review than large ones.

## Commit conventions
This repo follows [Conventional Commits](https://www.conventionalcommits.org/):
`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `ci:`.

## Code style
Python 3.11+, PEP 8, type hints on public functions. Run the test
suite locally before submitting (see [Testing](README.md#testing)).