"""Not part of the pytest suite — a manual end-to-end smoke test that
simulates real Ollama responses so we can verify the full agent pipeline
(all 8 stages + real file writes) without a live Ollama server.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from syj_ai.agent import SYJAgent
from syj_ai.config import SYJConfig
from syj_ai.models.base import ModelResponse

FAKE_CODE_RESPONSE = '''Here is the implementation:

```python:app/main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "hello from SYJ AI"}
```

```text:requirements.txt
fastapi
uvicorn
```
'''

with TemporaryDirectory() as tmp:
    config = SYJConfig(workspace=Path(tmp) / "workspace")
    agent = SYJAgent(config=config)

    call_count = {"n": 0}

    def fake_chat(role, messages):
        call_count["n"] += 1
        stage_label = messages[-1].content
        if "[Stage: Code]" in stage_label:
            content = FAKE_CODE_RESPONSE
        else:
            content = f"(simulated response #{call_count['n']} for: {stage_label.splitlines()[0]})"
        return ModelResponse(content=content, model="fake-model", backend="ollama")

    agent.router.chat = fake_chat  # monkeypatch for this smoke run

    result = agent.run("Build a tiny hello-world FastAPI app")

    assert len(result.stage_results) == 8, f"expected 8 stages, got {len(result.stage_results)}"
    code_stage = next(r for r in result.stage_results if r.stage.key == "code")
    assert "app/main.py" in code_stage.files_written
    assert "requirements.txt" in code_stage.files_written

    written = agent.workspace.read_file("app/main.py")
    assert "FastAPI" in written

    print("ALL STAGES:", [r.stage.key for r in result.stage_results])
    print("FILES WRITTEN:", code_stage.files_written)
    print("WORKSPACE CONTENTS:", agent.workspace.list_files())
    print("\nSMOKE TEST PASSED")
