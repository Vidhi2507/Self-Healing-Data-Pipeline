import pandas as pd
import matplotlib.pyplot as plt
import traceback
import json


def run_pipeline(path):
    try:
        df = pd.read_csv(path)

        today = pd.Timestamp.now()
        df["Age"] = pd.to_datetime(df["DOB"], errors="coerce")
        df["Age"] = (today - df["Age"]).dt.days // 365

        # Save cleaned data so ValidatorAgent can access it
        df.to_csv("data_check.csv", index=False)

        team_counts = df["TeamName"].value_counts()
        avg_age_by_team = df.groupby("TeamName")["Age"].mean()

        plt.figure(figsize=(8, 5))
        plt.hist(df["Age"].dropna(), bins=8, edgecolor="black")
        plt.title("Age Distribution")
        plt.savefig("age_distribution.png")
        plt.close()

        return {"success": True}

    except Exception as e:
        error_message = traceback.format_exc()

        with open("latest_error.json", "w") as f:
            json.dump({
                "error": error_message,
                "context": {"file_name": "Transformation.py"}
            }, f, indent=2)

        return {"success": False}


if __name__ == "__main__":
    run_pipeline()
