from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class DocumentParsingViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_process_document_view_minimal_case(self):
        # Minimal valid JSON to test basic functionality
        sample_json = {
            "type": "doc",
            "content": [
                {
                "type": "paperNode",
                "content": [
                    {
                    "type": "paperNameParagraph",
                    "attrs": {
                        "dataType": "paperName"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "introductionParagraph",
                    "attrs": {
                        "dataType": "introduction"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "theoryParagraph",
                    "attrs": {
                        "dataType": "theory"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "summaryParagraph",
                    "attrs": {
                        "dataType": "summary"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "paperURLParagraph",
                    "attrs": {
                        "dataType": "paperURL"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    }
                ]
                },
                {
                "type": "experimentNode",
                "content": [
                    {
                    "type": "experimentNameParagraph",
                    "attrs": {
                        "dataType": "experimentName"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "taskContextParagraph",
                    "attrs": {
                        "dataType": "taskContext"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "taskParagraph",
                    "attrs": {
                        "dataType": "task"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "taskExplainedParagraph",
                    "attrs": {
                        "dataType": "taskExplained"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "discussionParagraph",
                    "attrs": {
                        "dataType": "discussion"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "experimentURLParagraph",
                    "attrs": {
                        "dataType": "experimentURL"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    }
                ]
                },
                {
                "type": "measurementNode",
                "attrs": {
                    "measurementType": "brodmann"
                },
                "content": [
                    {
                    "type": "mDescriptionParagraph",
                    "attrs": {
                        "dataType": "mDescription"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "mParametersParagraph",
                    "attrs": {
                        "dataType": "mParameters"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "mInterpretationParagraph",
                    "attrs": {
                        "dataType": "mInterpertation"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "mLabelParagraph",
                    "attrs": {
                        "dataType": "mLabel"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    },
                    {
                    "type": "brodmannAreaParagraph",
                    "attrs": {
                        "placeholder": "Brodmann Area",
                        "dataType": "integer"
                    },
                    "content": [
                        {
                        "type": "text",
                        "text": " parse"
                        }
                    ]
                    }
                ]
                }
            ]
        }
        response = self.client.post(reverse('process_document'), sample_json, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'success')