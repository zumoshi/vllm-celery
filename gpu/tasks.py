import os
from typing import List

from celery import Celery
from openai import OpenAI

app = Celery(
    "tasks",
    broker=f"amqp://gpu:{os.environ['RABBIT_PW']}@{os.environ['RABBIT_HOST']}//",
)

MODE = os.environ.get("MODE", 'batch')
MODEL = os.environ.get("VLLM_MODEL", "google/gemma-3n-e4b-it")
MAX_TOKENS = 2**13

app.conf.update(
    worker_concurrency=2,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

def strip_non_json(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return text
    return text[start:end+1]

@app.task
def run_on_llm(result_task_name: str, system_prompt: str, batch: list[tuple[int, str]]) -> None:
    if MODE == "batch":
        answer = run_on_llm_batch(system_prompt, batch)
    else:
        answer = run_on_llm_sequential(system_prompt, batch)

    answer_with_key = [
        (k[0], strip_non_json(v)) for k, v in zip(batch, answer)
    ]

    app.send_task(
        result_task_name,
        args=(answer_with_key,),
    )


def run_on_llm_batch(system_prompt: str, batch: list[tuple[int, str]]) -> List[str]:
    client = OpenAI(
        base_url="http://127.0.0.1:18000/v1",
        api_key='blah',
    )

    return [x.text.strip() for x in client.completions.create(
        model=MODEL,
        prompt=[system_prompt + p for _, p in batch],
        temperature=0,
        max_tokens=MAX_TOKENS,
    ).choices]


def run_on_llm_sequential(system_prompt: str, batch: list[tuple[int, str]]) -> List[str]:
    client = OpenAI(
        base_url="http://127.0.0.1:18000/v1",
        api_key='blah',
    )

    answer = []
    for _, p in batch:
        answer.append(client.completions.create(
            model=MODEL,
            prompt=system_prompt + p,
            temperature=0,
            max_tokens=MAX_TOKENS,
        ).choices[0].text.strip())

    return answer
