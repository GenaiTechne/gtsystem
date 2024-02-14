import pandas as pd
TASKS = None

def get(task = ''):
    system = TASKS[TASKS['Task'] == task]['System'].values[0]
    prompt = TASKS[TASKS['Task'] == task]['Prompt'].values[0]
    temperature = float(TASKS[TASKS['Task'] == task]['Temperature'].values[0])
    topP = float(TASKS[TASKS['Task'] == task]['TopP'].values[0])
    return system, prompt, temperature, topP

def list(start=1, end=5):
    return TASKS.iloc[start:end]

def find(task='', type='', prompt='', source=''):
    if type != '':
        df = TASKS[TASKS['Task Types'].str.contains(type, case=False)]
    elif task != '':
        df = TASKS[TASKS['Task'].str.contains(task, case=False)]
    elif prompt != '':
        df = TASKS[TASKS['Prompt'].str.contains(prompt, case=False)]
    elif source != '':
        df = TASKS[TASKS['Source'].str.contains(source, case=False)]
    return df

def load(prompts_file):
    global TASKS
    df = pd.read_excel(prompts_file)
    TASKS = df
