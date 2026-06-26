from knowledge_base.indexer import KnowledgeIndexer


def test_chunking_overlaps_text():
    indexer = KnowledgeIndexer(chunk_size=10, chunk_overlap=2)

    chunks = indexer._chunk("abcdefghijklmnopqrstuvwxyz")

    assert chunks == ["abcdefghij", "ijklmnopqr", "qrstuvwxyz"]


def test_record_to_text_skips_none_values():
    indexer = KnowledgeIndexer()

    text = indexer._record_to_text({"name": "Project A", "empty": None})

    assert "name: Project A" in text
    assert "empty" not in text
