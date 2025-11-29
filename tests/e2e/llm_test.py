from standupbrain.llm import prompt_local_llm


def test_prompt_local_llm() -> None:
    """This is obviously not totally deterministic but it passes reliably"""
    result = prompt_local_llm('Just say "Hi!"')
    assert result == 'Hi!'
