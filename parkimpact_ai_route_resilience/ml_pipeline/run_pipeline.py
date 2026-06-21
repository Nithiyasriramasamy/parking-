import subprocess

def run_all():
    print("Running full ML pipeline...")
    subprocess.run(["python", "train_occlusion.py"])
    subprocess.run(["python", "train_tgcn.py"])
    print("Pipeline complete.")

if __name__ == "__main__":
    run_all()
