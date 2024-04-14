import json
from venv import logger
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from .instrument import metrics
from .chat import ClaudeChat

BEDROCK_RUNTIME = None
BEDROCK = None

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

def _init():
    global BEDROCK
    BEDROCK = _get_client(
        assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
        region=os.environ.get("AWS_DEFAULT_REGION", None),
        runtime=False
    )

def list_models(vendor):
    if BEDROCK is None:
        _init()
    listModels = BEDROCK.list_foundation_models(byProvider=vendor)
    print("\n".join(list(map(lambda x: f"{x['modelName']} : { x['modelId'] }", listModels['modelSummaries']))))

CHAT_CONTEXT = ClaudeChat()

def _claude3_chat(prompt, system='', temperature=0.0, topP=1, tokens=4096, model="", image_url="", reset=False):
    if reset:
        CHAT_CONTEXT.reset_context()
    
    if system != "":
        CHAT_CONTEXT.set_system(system)
    
    if image_url != "":
        CHAT_CONTEXT.add_image_message(image_url=image_url, prompt=prompt)
    else:
        CHAT_CONTEXT.add_message("user", prompt)

    try:
        if BEDROCK_RUNTIME is None:
            _init_runtime()

        response = BEDROCK_RUNTIME.invoke_model(
            modelId=model,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "system": CHAT_CONTEXT.get_system(),
                    "max_tokens": tokens,
                    "temperature": temperature,
                    "top_p": topP,
                    "max_tokens": tokens,
                    "messages": CHAT_CONTEXT.get_messages(),
                }
            ),
        )

        result = json.loads(response.get('body').read())
        CHAT_CONTEXT.add_message("assistant", result['content'][0]['text'])

        return result['content'][0]['text']

    except ClientError as err:
        logger.error(
            "Couldn't invoke Claude 3. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise


@metrics.track
def sonnet_chat(prompt, system='', temperature=0.0, topP=1.0, tokens=512, image_url="", reset=False):
    return _claude3_chat(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='anthropic.claude-3-sonnet-20240229-v1:0', 
                         image_url=image_url, reset=reset)

@metrics.track
def haiku_chat(prompt, system='', temperature=0.0, topP=1.0, tokens=512, image_url="", reset=False):
    return _claude3_chat(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='anthropic.claude-3-haiku-20240307-v1:0', 
                         image_url=image_url, reset=reset)

def _claude3_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512, model=''):
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

@metrics.track
def sonnet_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512):
    return _claude3_text(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='anthropic.claude-3-sonnet-20240229-v1:0')

@metrics.track
def haiku_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512):
    return _claude3_text(prompt, system=system, 
                         temperature=temperature, topP=topP, tokens=tokens, 
                         model='anthropic.claude-3-haiku-20240307-v1:0')

def _claude2_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512, model=''):

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
            _init_runtime()

        response = BEDROCK_RUNTIME.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())
        response_text = response_body.get("completion").strip()
    
        return response_text
    
    except ClientError as error:
    
        if error.response['Error']['Code'] == 'AccessDeniedException':
               print(f"\x1b[41m{error.response['Error']['Message']}\
                    \nTo troubeshoot this issue please refer to the following resources.\
                     \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                     \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n")
    
        else:
            raise error

@metrics.track        
def claude2_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512):
    return _claude2_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512, model='anthropic.claude-v2:1')

@metrics.track        
def instant_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512):
    return _claude2_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512, model='anthropic.claude-instant-v1')

@metrics.track        
def llama2_text(prompt, system='', temperature=0.0, topP=1.0, tokens=512, model='meta.llama2-70b-chat-v1'):

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
            _init_runtime()

        response = BEDROCK_RUNTIME.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get('body').read().decode('utf-8'))
        response_text = response_body['generation'].strip()
    
        return response_text
    
    except ClientError as error:
    
        if error.response['Error']['Code'] == 'AccessDeniedException':
               print(f"\x1b[41m{error.response['Error']['Message']}\
                    \nTo troubeshoot this issue please refer to the following resources.\
                     \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                     \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n")
    
        else:
            raise error

def text(prompt, system='', temperature=0.0, topP=1.0, tokens=512, model='sonnet'):
    match model:
        case 'sonnet':
            return sonnet_text(prompt, system, temperature, topP, tokens)
        case 'haiku':
            return haiku_text(prompt, system, temperature, topP, tokens)
        case 'claude2':
            return claude2_text(prompt, system, temperature, topP, tokens)
        case 'instant':
            return instant_text(prompt, system, temperature, topP, tokens)
        case 'llama2':
            return llama2_text(prompt, system, temperature, topP, tokens)
        case _:
            return 'Please specify a valid model name'
