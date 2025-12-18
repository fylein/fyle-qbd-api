import os
import boto3
import openai
import json
from typing import Dict


AWS_REGION = os.environ["AWS_REGION"]
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]


bedrock_session = boto3.Session(
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

openai_client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    max_retries=5,
    timeout=10
)


def get_openai_response(*, system_prompt: str) -> dict:
    try:
        chat_completion_resp = openai_client.chat.completions.create(
            model="gpt-4o",
            response_format={
                "type": "json_object"
            },
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0,
            max_tokens=256,
            top_p=0,
            frequency_penalty=0,
            presence_penalty=0
        )

        return json.loads(
            chat_completion_resp.choices[0].message.content
        )

    except (openai.OpenAIError, json.JSONDecodeError) as e:
        raise Exception(message=str(e))



def get_support_response_from_bedrock(*, prompt_template: str, input_message: str) -> Dict:
    try:
        bedrock_agent_runtime_client = bedrock_session.client(
            'bedrock-agent-runtime'
        )

        response = bedrock_agent_runtime_client.retrieve_and_generate(
            input={
                'text': input_message
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': 'arn:aws:bedrock:ap-south-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0',
                    'generationConfiguration': {
                        'inferenceConfig': {
                            'textInferenceConfig': {
                                'maxTokens': 2048,
                                'stopSequences': [],
                                'temperature': 0,
                                'topP': 1
                            }
                        },
                        'promptTemplate': {
                            'textPromptTemplate': prompt_template
                        }
                    },
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': 5,
                            'overrideSearchType': 'HYBRID',
                        }
                    }
                }
            }
        )

        return response

    except json.JSONDecodeError as e:
        print(e)
