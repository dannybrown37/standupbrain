from datetime import datetime
import logging
import sys
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

from standupbrain.jira_init import get_jira_credentials


log = logging.getLogger(__name__)


def make_jira_activity_summary(date: datetime) -> str:
    """Entry point function for CLI to get Jira activity summary"""
    response = get_my_jira_activity(date)
    return format_activity_for_llm(response, date)


def get_my_jira_activity(date: datetime) -> dict:
    """Query current user's Jira activity (requires env vars to be set)"""
    credentials = get_jira_credentials()
    if not credentials:
        log.error('Run `standupbrain init` first')
        sys.exit(1)

    base_url, email, api_token = credentials
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    jql = f'assignee = currentUser() AND updated >= "{date.strftime("%Y-%m-%d")}"'
    params = {
        'jql': jql,
        'fields': 'summary,description,status,updated,comment',
        'maxResults': 100,
    }
    response = requests.get(
        urljoin(base_url, '/rest/api/3/search/jql'),
        headers=headers,
        params=params,
        auth=HTTPBasicAuth(email, api_token),
    )
    log.debug(response.text)
    response.raise_for_status()
    return response.json()


def extract_text_from_adf(content: list) -> str:
    """Parse Atlassian Document Format (ADF) to readable text"""
    text_parts = []
    for block in content:
        if block.get('type') == 'paragraph':
            for item in block.get('content', []):
                if item.get('type') == 'text':
                    text_parts.append(item['text'])
                elif item.get('type') == 'mention':
                    text_parts.append(item['attrs']['text'])
        elif block.get('type') == 'text':
            text_parts.append(block['text'])
    return ''.join(text_parts)


def format_activity_for_llm(data: dict, target_date: datetime) -> str:
    """Format Jira activity for LLM prompt"""
    issues = data.get('issues', [])
    if not issues:
        log.debug('No Jira activity found for %s', target_date)
        return ''

    log.debug('Formatting Jira activity for LLM')
    issues = []
    target_date = target_date.strftime('%Y-%m-%d')

    for issue in issues:
        fields = issue['fields']
        key = issue['key']
        summary = fields['summary']
        status = fields['status']['name']

        description = extract_text_from_adf(
            fields.get('description', {}).get('content', []),
        )

        comments_on_date = []
        for comment in fields.get('comment', {}).get('comments', []):
            created = comment['created'][:10]
            if created == target_date:
                text = extract_text_from_adf(comment['body'].get('content', []))
                comments_on_date.append(f'  - {text}')

        if comments_on_date:
            issue_summary = f'[{key}] {summary}\nStatus: {status}\n'
            if description:
                issue_summary += f'Description: {description}\n'
            issue_summary += 'Comments:\n' + '\n'.join(comments_on_date)
            issues.append(issue_summary)

    result = '\n\n'.join(issues)
    log.debug('Jira summary:\n%s', result)
    return result
