from app.services.change_detector import classify, hash_content


def test_hash_content_same_input_same_hash():
    assert hash_content("hello world") == hash_content("hello world")


def test_hash_content_different_input_different_hash():
    assert hash_content("hello world") != hash_content("goodbye world")


def test_new_when_source_path_absent_from_known_hashes():
    batch = {"docs/a.md": "content a"}
    known_hashes: dict[str, str] = {}

    result = classify(batch, known_hashes)

    assert result == {"docs/a.md": "new"}


def test_unchanged_when_hash_matches():
    batch = {"docs/a.md": "content a"}
    known_hashes = {"docs/a.md": hash_content("content a")}

    result = classify(batch, known_hashes)

    assert result == {"docs/a.md": "unchanged"}


def test_changed_when_hash_differs():
    batch = {"docs/a.md": "content a v2"}
    known_hashes = {"docs/a.md": hash_content("content a v1")}

    result = classify(batch, known_hashes)

    assert result == {"docs/a.md": "changed"}


def test_removed_when_source_path_absent_from_batch():
    batch: dict[str, str] = {}
    known_hashes = {"docs/a.md": hash_content("content a")}

    result = classify(batch, known_hashes)

    assert result == {"docs/a.md": "removed"}


def test_empty_batch_with_known_hashes_marks_everything_removed():
    batch: dict[str, str] = {}
    known_hashes = {
        "docs/a.md": hash_content("content a"),
        "docs/b.md": hash_content("content b"),
    }

    result = classify(batch, known_hashes)

    assert result == {"docs/a.md": "removed", "docs/b.md": "removed"}


def test_empty_known_hashes_marks_everything_new():
    batch = {"docs/a.md": "content a", "docs/b.md": "content b"}
    known_hashes: dict[str, str] = {}

    result = classify(batch, known_hashes)

    assert result == {"docs/a.md": "new", "docs/b.md": "new"}


def test_identical_content_under_different_paths_classified_independently_as_new():
    batch = {"docs/a.md": "same content", "docs/b.md": "same content"}
    known_hashes: dict[str, str] = {}

    result = classify(batch, known_hashes)

    assert result == {"docs/a.md": "new", "docs/b.md": "new"}


def test_identical_content_under_different_paths_classified_independently_mixed():
    batch = {"docs/a.md": "same content", "docs/b.md": "same content"}
    known_hashes = {"docs/a.md": hash_content("same content")}

    result = classify(batch, known_hashes)

    assert result == {"docs/a.md": "unchanged", "docs/b.md": "new"}
