import pandas as pd
TASKS = None

def get(task = ''):
    system = TASKS[TASKS['Task'] == task]['System'].values[0]
    prompt = TASKS[TASKS['Task'] == task]['Prompt'].values[0]
    return prompt, system

def list(start=1, end=5):
    return TASKS.iloc[start:end]

def find(task='', prompt=''):
    if task != '':
        df = TASKS[TASKS['Task'].str.contains(task, case=False)]
    elif prompt != '':
        df = TASKS[TASKS['Prompt'].str.contains(prompt, case=False)]
    return df

def load(prompts_file):
    global TASKS
    df = pd.read_excel(prompts_file)
    TASKS = df
