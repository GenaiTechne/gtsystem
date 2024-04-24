import json
from venv import logger
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from .chat import ClaudeChat

BEDROCK_RUNTIME = None

def _get_client(assumed_role=None, region=None, runtime=True):
    if region is None:
        target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
    else:
        target_region = region

    session_kwargs = {"region_name": target_region}
    client_kwargs = {**session_kwargs}

    profile_name = os.environ.get("AWS_PROFILE")
    if profile_name:
        session_kwargs["profile_name"] = profile_name

    retry_config = Config(
        region_name=target_region,
        retries={
            "max_attempts": 10,
            "mode": "standard",
        },
    )
    session = boto3.Session(**session_kwargs)

    if assumed_role:
        sts = session.client("sts")
        response = sts.assume_role(
            RoleArn=str(assumed_role),
            RoleSessionName="langchain-llm-1"
        )
        client_kwargs["aws_access_key_id"] = response["Credentials"]["AccessKeyId"]
        client_kwargs["aws_secret_access_key"] = response["Credentials"]["SecretAccessKey"]
        client_kwargs["aws_session_token"] = response["Credentials"]["SessionToken"]

    if runtime:
        service_name='bedrock-runtime'
    else:
        service_name='bedrock'

    bedrock_client = session.client(
        service_name=service_name,
        config=retry_config,
        **client_kwargs
    )

    return bedrock_client

def _init_runtime():
    global BEDROCK_RUNTIME
    BEDROCK_RUNTIME = _get_client(
        assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
        region=os.environ.get("AWS_DEFAULT_REGION", None)
    )

MODELS = {
    'sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'haiku': 'anthropic.claude-3-haiku-20240307-v1:0'
}

CHAT = ClaudeChat()

def chat(prompt, system='', temperature=0.0, topP=1, tokens=4096, image_url="", 
         reset=False, cache=False, model=MODELS['sonnet']):
    if cache:
        cache_match = CHAT.match(prompt)
        if cache_match:
            CHAT.load(cache_match)
            return next(msg['content'] for msg in CHAT.messages if msg['role'] == 'assistant')

    if reset:
        CHAT.reset_context()
    
    if system != "":
        CHAT.set_system(system)
    
    if image_url != "":
        CHAT.add_image_message(image_url=image_url, prompt=prompt)
    else:
        CHAT.add_message("user", prompt)

    try:
        if BEDROCK_RUNTIME is None:
            _init_runtime()

        response = BEDROCK_RUNTIME.invoke_model(
            modelId=model,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "system": CHAT.get_system(),
                    "max_tokens": tokens,
                    "temperature": temperature,
                    "top_p": topP,
                    "max_tokens": tokens,
                    "messages": CHAT.get_messages(),
                }
            ),
        )

        result = json.loads(response.get('body').read())
        CHAT.add_message("assistant", result['content'][0]['text'])

        return result['content'][0]['text']

    except ClientError as err:
        logger.error(
            "Couldn't invoke Claude 3. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

def text(prompt, system='', temperature=0.0, topP=1.0, tokens=512, 
         model=MODELS['sonnet']):
    try:
        if BEDROCK_RUNTIME is None:
            _init_runtime()

        response = BEDROCK_RUNTIME.invoke_model(
            modelId=model,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "system": system,
                    "temperature": temperature,
                    "top_p": topP,
                    "max_tokens": tokens,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": prompt}],
                        }
                    ],
                }
            ),
        )

        result = json.loads(response.get('body').read())
        return result['content'][0]['text']

    except ClientError as err:
        logger.error(
            "Couldn't invoke Claude 3. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise