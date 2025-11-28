import subprocess

from standupbrain.shared import OLLAMA_MODEL


def create_standup_summary_llm_prompt(commits: list[dict]) -> str:
    content = (
        'I am including the commits from my last workday here.'
        'Your task is to create a summary of the commits for each repo that '
        'I can reference in standup to help me remember what I did. '
        'Bullet point format is fine. Being concise and accurate is crucial. '
        'Do not reprint/refactor any code. Just summarize the code I added. '
        'Try to limit to five bullet points max, unless truly justified to '
        'exceed this count'
        '\n\n'
    )
    for commit_data in commits:
        content += f'Repo: {commit_data["repo"]}\n{commit_data["output"]}\n\n'
    return content


def prompt_local_llm(prompt: str) -> str:
    result = subprocess.run(
        ['ollama', 'run', OLLAMA_MODEL, prompt],
        check=True,
    )
    return result.stdout
