from app.services.chunker import chunk


def test_empty_content_returns_no_chunks():
    assert chunk("") == []


def test_content_shorter_than_chunk_size_returns_single_chunk():
    content = "one two three"
    assert chunk(content, chunk_size=200, overlap=40) == [content]


def test_content_longer_than_chunk_size_returns_multiple_chunks():
    words = [f"word{i}" for i in range(250)]
    content = " ".join(words)

    pieces = chunk(content, chunk_size=200, overlap=40)

    assert len(pieces) == 2
    assert pieces[0] == " ".join(words[0:200])
    assert pieces[1] == " ".join(words[160:250])


def test_consecutive_chunks_share_overlap_words():
    words = [f"word{i}" for i in range(250)]
    content = " ".join(words)

    pieces = chunk(content, chunk_size=200, overlap=40)

    tail_of_first = pieces[0].split()[-40:]
    head_of_second = pieces[1].split()[:40]
    assert tail_of_first == head_of_second


def test_doubling_word_count_roughly_doubles_chunk_count():
    words = [f"word{i}" for i in range(200)]
    single = " ".join(words)
    doubled = " ".join(words * 2)

    single_count = len(chunk(single, chunk_size=50, overlap=10))
    doubled_count = len(chunk(doubled, chunk_size=50, overlap=10))

    assert doubled_count > single_count
