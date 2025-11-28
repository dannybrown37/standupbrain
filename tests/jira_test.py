from datetime import datetime

import pytest

from standupbrain.jira import extract_text_from_adf, format_activity_for_llm


@pytest.mark.parametrize(
    ('content', 'expected'),
    [
        (
            [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Hello'}]}],
            'Hello',
        ),
        (
            [
                {
                    'type': 'paragraph',
                    'content': [
                        {'type': 'text', 'text': 'Hi '},
                        {'type': 'mention', 'attrs': {'text': '@user'}},
                    ],
                },
            ],
            'Hi @user',
        ),
        ([{'type': 'text', 'text': 'Direct text'}], 'Direct text'),
        ([], ''),
    ],
)
def test_extract_text_from_adf(content: list, expected: str) -> None:
    assert extract_text_from_adf(content) == expected


def test_format_activity_for_llm_no_issues() -> None:
    data = {'issues': []}
    result = format_activity_for_llm(data, datetime(2025, 11, 26))
    assert result == ''


def test_format_activity_for_llm_with_comments() -> None:
    data = {
        'issues': [
            {
                'key': 'TEST-123',
                'fields': {
                    'summary': 'Test issue',
                    'status': {'name': 'Done'},
                    'description': {
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [{'type': 'text', 'text': 'Desc'}],
                            },
                        ],
                    },
                    'comment': {
                        'comments': [
                            {
                                'created': '2025-11-26T10:00:00.000-0500',
                                'body': {
                                    'content': [
                                        {
                                            'type': 'paragraph',
                                            'content': [
                                                {'type': 'text', 'text': 'Comment'},
                                            ],
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                    'updated': '2025-11-26T10:00:00.000-0500',
                },
            },
        ],
    }
    result = format_activity_for_llm(data, datetime(2025, 11, 26))
    assert '[TEST-123]' in result
    assert 'Test issue' in result
    assert 'Comment' in result


def test_format_activity_for_llm_filters_by_date() -> None:
    data = {
        'issues': [
            {
                'key': 'TEST-123',
                'fields': {
                    'summary': 'Test',
                    'status': {'name': 'Done'},
                    'comment': {
                        'comments': [
                            {
                                'created': '2025-11-25T10:00:00.000-0500',
                                'body': {'content': []},
                            },
                        ],
                    },
                    'updated': '2025-11-25T10:00:00.000-0500',
                },
            },
        ],
    }
    result = format_activity_for_llm(data, datetime(2025, 11, 26))
    assert result == ''
