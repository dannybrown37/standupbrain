from conftest import skip_90_percent_for_slower_tests

from standupbrain.llm import prompt_local_llm


@skip_90_percent_for_slower_tests
def test_prompt_local_llm() -> None:
    result = prompt_local_llm('Just say "Hi!"')
    assert result == 'Hi!'
