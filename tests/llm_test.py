from standupbrain.llm import prompt_local_llm


def test_prompt_local_llm() -> None:
    result = prompt_local_llm('Just say "Hi!"')
    assert result == 'Hi!'
