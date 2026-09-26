import asyncio
import time
import os
from app.agent.executor import agent_executor

html_path = 'workspace/test_workbench.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html>
<head><title>Sovereign Refinery Dashboard</title></head>
<body>
<h1>Refinery Unit 4 Inspection Report</h1>
<p>Valve pressure is 450 PSI. Flange gasket maintenance is recommended by Q4.</p>
<button>Approve Maintenance</button>
</body>
</html>""")

async def test_flow():
    with open("memory_test_log.txt", "w", encoding="utf-8") as out:
        out.write("--- Run 1: Universal File Extractor Analysis ---\n")
        t0 = time.time()
        res1 = await agent_executor.run_agent_workflow("task_t1", "tell me about this file", file_paths=[html_path])
        t1 = time.time() - t0
        out.write(f"Run 1 Completed in {t1:.2f}s | Model: {res1['model_used']}\n")
        out.write(f"Output Sample:\n{res1['output'][:400]}\n\n")

        out.write("--- Run 2: Pattern Recognition Memory Match (Ultra-Fast) ---\n")
        t0 = time.time()
        res2 = await agent_executor.run_agent_workflow("task_t2", "tell me about this file", file_paths=[html_path])
        t2 = time.time() - t0
        out.write(f"Run 2 Completed in {t2:.5f}s | Model: {res2['model_used']}\n")
        out.write(f"Output Sample:\n{res2['output'][:400]}\n")

    print("Wrote memory_test_log.txt successfully!")

if __name__ == '__main__':
    asyncio.run(test_flow())
