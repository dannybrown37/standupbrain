import subprocess

from standupbrain.shared import OLLAMA_MODEL

PROMPT = """
You are a helpful assistant that reminds me what I did the prior work
day for standup purposes. I'm including the commits for all code changes I
made that day. I need you to summarize in 3-5 bullet points what I did.
Make each bullet point a high-level overview such as "Changed behavior of X",
"tidied Y", "fixed Z", etc. Don't get too in the weeds about the finer
details, keep it broad, human-like, and appropriate for standup.
"""


def create_standup_summary_llm_prompt(jira_summary: str, commits: list[dict]) -> str:
    content = PROMPT + '\nHere is a summary of Jira activity:\n' + jira_summary
    content += '\n\nHere are the commits for the day:\n'
    for commit_data in commits:
        content += f'Repo: {commit_data["repo"]}\n{commit_data["output"]}\n\n'
    return content


def prompt_local_llm(prompt: str) -> str:
    result = subprocess.run(
        ['ollama', 'run', OLLAMA_MODEL, prompt],
        check=True,
    )
    return result.stdout
