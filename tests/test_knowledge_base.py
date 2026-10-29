
import pytest

from forgebid.knowledge_base import split_into_chunks


def test_short_text_returns_one_chunk():
    text = "ForgeBid analyzes RFP requirements."

    chunks = split_into_chunks(text)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_long_text_is_split_into_chunks():
    text = "one two three four five six"

    chunks = split_into_chunks(
        text,
        chunk_size=4,
        overlap=1,
    )

    assert chunks == [
        "one two three four",
        "four five six",
    ]


def test_empty_text_returns_no_chunks():
    assert split_into_chunks("") == []


def test_chunks_preserve_all_words():
    text = "alpha beta gamma delta epsilon"

    chunks = split_into_chunks(
        text,
        chunk_size=3,
        overlap=1,
    )

    reconstructed_words = []

    for chunk in chunks:
        reconstructed_words.extend(chunk.split())

    # Every original word must appear in order.
    assert reconstructed_words == [
        "alpha", "beta", "gamma",
        "gamma", "delta", "epsilon",
    ]


def test_zero_chunk_size_is_rejected():
    with pytest.raises(ValueError):
        split_into_chunks("some text", chunk_size=0)


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        split_into_chunks(
            "some text",
            chunk_size=3,
            overlap=3,
        )


def test_negative_overlap_is_rejected():
    with pytest.raises(ValueError):
        split_into_chunks(
            "some text",
            chunk_size=3,
            overlap=-1,
        )
