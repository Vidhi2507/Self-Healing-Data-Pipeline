import pandas as pd


async def run_validation():
    try:
        df = pd.read_csv("data_check.csv")

        if df["DOB"].isna().any():
            return {"status": "fail", "reason": "Invalid dates remain"}

        if (df["Age"] < 0).any():
            return {"status": "fail", "reason": "Negative ages present"}

        return {"status": "success", "message": "Data looks good"}

    except Exception as e:
        return {"status": "fail", "reason": str(e)}
