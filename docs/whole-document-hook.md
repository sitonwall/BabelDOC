# Downstream whole-document translation hook

This branch follows upstream BabelDOC 0.6.4 and preserves its AGPL-3.0 license.
It carries two changes: long-identifier line wrapping and an explicit Python API
callback. The word-wrap fix is isolated on `fix/long-identifier-line-wrapping`
for upstream review. The callback remains a downstream extension.

Pass `document_translator=callback`, `auto_extract_glossary=False`, and
`split_strategy=None` to `TranslationConfig`. The callback receives the prepared
`il_version_1.Document` and its `TranslationConfig` after paragraph/formula/style
extraction, before translation and typesetting. Update the IR in place and return
`None`. Normal typesetting and mono/dual output generation then continue.

The callback owns its requests, budgets, cancellation, validation, and mapping.
It bypasses legacy translator initialization and automatic term extraction.
Callback exceptions propagate; they never trigger legacy translation as a
fallback. Combining the callback with translation skipping, automatic glossary
extraction, or page splitting is rejected. With the default `None`, the ordinary
translator path is preserved.

The associated opt-in service and setup instructions live in
[sitonwall/zotero-pdf2zh](https://github.com/sitonwall/zotero-pdf2zh/tree/whole-document).
Use an immutable commit when depending on this fork. No secrets or model calls
are required to run the regression tests:

```sh
python -m unittest discover -s tests -v
ruff check .
```

Four local regressions cover line wrapping, callback dispatch, callback failure,
and the default legacy path. A real-paper experiment on an earlier 0.6.2-based
backport is downstream evidence, not a current-main live translation guarantee.
