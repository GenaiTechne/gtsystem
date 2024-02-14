import json
import botocore
import time
import os

import boto3
from botocore.config import Config

from .instrument import instrument

LLAMA_ACCURACY = 0
CLAUDE_ACCURACY = 0

BEDROCK_RUNTIME = None
BEDROCK = None

def get_client(assumed_role=None, region=None, runtime=True):
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

def init_runtime():
    global BEDROCK_RUNTIME
    BEDROCK_RUNTIME = get_client(
        assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
        region=os.environ.get("AWS_DEFAULT_REGION", None)
    )

def init():
    global BEDROCK
    BEDROCK = get_client(
        assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
        region=os.environ.get("AWS_DEFAULT_REGION", None),
        runtime=False
    )

def list_models(vendor):
    if BEDROCK is None:
        init()
    listModels = BEDROCK.list_foundation_models(byProvider=vendor)
    print("\n".join(list(map(lambda x: f"{x['modelName']} : { x['modelId'] }", listModels['modelSummaries']))))

@instrument.track
def claude_text(system='', prompt='', temperature=0.0, topP=1.0, tokens=512, model='anthropic.claude-v2:1'):

    decorated_prompt = f'Human: {(system + " " + prompt).strip()}\n\nAssistant:\n'
    body = json.dumps({"prompt": decorated_prompt, 
                       "temperature": temperature,
                       "top_p": topP,
                       "max_tokens_to_sample": tokens})
    modelId = model
    accept = "application/json"
    contentType = "application/json"
    
    try:
        if BEDROCK_RUNTIME is None:
            init_runtime()

        response = BEDROCK_RUNTIME.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())
        response_text = response_body.get("completion").strip()
    
        return response_text
    
    except botocore.exceptions.ClientError as error:
    
        if error.response['Error']['Code'] == 'AccessDeniedException':
               print(f"\x1b[41m{error.response['Error']['Message']}\
                    \nTo troubeshoot this issue please refer to the following resources.\
                     \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                     \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n")
    
        else:
            raise error

@instrument.track        
def llama_text(system='', prompt='', temperature=0.0, topP=1.0, tokens=512, model='meta.llama2-70b-chat-v1'):

    if system != '':
        decorated_prompt = f'<<SYS>>{system}<</SYS>>\n[INST]User:{prompt}[/INST]\nAssistant:'
    else:
        decorated_prompt = prompt

    body = json.dumps({ 
        'prompt': decorated_prompt,
        'max_gen_len': tokens,
        'top_p': topP,
        'temperature': temperature
    })

    modelId = model
    accept = "application/json"
    contentType = "application/json"
    
    try:
        if BEDROCK_RUNTIME is None:
            init_runtime()

        response = BEDROCK_RUNTIME.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get('body').read().decode('utf-8'))
        response_text = response_body['generation'].strip()
    
        return response_text
    
    except botocore.exceptions.ClientError as error:
    
        if error.response['Error']['Code'] == 'AccessDeniedException':
               print(f"\x1b[41m{error.response['Error']['Message']}\
                    \nTo troubeshoot this issue please refer to the following resources.\
                     \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                     \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n")
    
        else:
            raise error

