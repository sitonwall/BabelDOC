"""Test the opt-in document translation seam without sending model requests."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import patch

from babeldoc.format.pdf.document_il.il_version_1 import Document
from babeldoc.format.pdf.high_level import _translate_document


class DocumentTranslatorTest(unittest.TestCase):
    """Callbacks own translation and cannot fall through to legacy translators."""

    def test_callback_bypasses_legacy_translators_and_term_extraction(self) -> None:
        """Dispatch the complete IR exactly once before any legacy setup."""
        docs = Document()
        callback = Mock()
        config = SimpleNamespace(
            document_translator=callback,
            skip_translation=False,
            auto_extract_glossary=False,
        )
        with (
            patch("babeldoc.format.pdf.high_level.ILTranslator") as legacy,
            patch("babeldoc.format.pdf.high_level.AutomaticTermExtractor") as terms,
        ):
            _translate_document(docs, config)
        callback.assert_called_once_with(docs, config)
        legacy.assert_not_called()
        terms.assert_not_called()

    def test_callback_failure_does_not_start_legacy_translation(self) -> None:
        """An explicit callback failure must propagate to its caller."""
        callback = Mock(side_effect=RuntimeError("fixture failure"))
        config = SimpleNamespace(document_translator=callback)
        with (
            patch("babeldoc.format.pdf.high_level.ILTranslator") as legacy,
            self.assertRaisesRegex(RuntimeError, "fixture failure"),
        ):
            _translate_document(Document(), config)
        legacy.assert_not_called()

    def test_default_legacy_path_still_translates(self) -> None:
        """The default path preserves legacy behavior and valid debug logging."""
        docs = Document()
        config = SimpleNamespace(
            document_translator=None,
            translator=Mock(),
            get_term_extraction_translator=Mock(return_value=Mock()),
            auto_extract_glossary=False,
            skip_translation=False,
        )
        with (
            patch(
                "babeldoc.format.pdf.high_level.translator_supports_llm",
                return_value=False,
            ),
            patch("babeldoc.format.pdf.high_level.ILTranslator") as legacy,
        ):
            _translate_document(docs, config)
        legacy.return_value.translate.assert_called_once_with(docs)


if __name__ == "__main__":
    unittest.main()
