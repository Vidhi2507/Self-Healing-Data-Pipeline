# orchestrator.py
import asyncio
import json
from Transformation import run_pipeline
from DiagnosticAgent import run_diagnostic
from RepairAgent import run_repair
from ValidatorAgent import run_validation


async def orchestrator(path: str):

    MAX_ITERS = 5

    for i in range(1, MAX_ITERS + 1):
        print(f"\n🔁 ITERATION {i} — Running Transformation Pipeline...\n")

        t = run_pipeline(path)

        if not t["success"]:
            print("\n❗ Error detected — running Diagnosis Agent...")
            with open("latest_error.json") as f:
                payload = json.load(f)

            diagnosis = await run_diagnostic(payload)
            print("Diagnosis:", diagnosis)

            print("\n🛠 Running Repair Agent...")
            await run_repair(diagnosis)
            continue

        print("✔ Transformation successful. No errors detected.\n")

        # Run Validator
        validation = await run_validation()
        print("Validation:", validation)

        if validation.get("status") == "success":
            print("\n🎉 Pipeline healed successfully! Exiting...\n")
            return
        else:
            print("\n⚠ Validation failed. Running healing cycle...\n")

    print("\n❌ Max iterations reached — pipeline still not healthy.")

asyncio.run(orchestrator("data_check.csv"))