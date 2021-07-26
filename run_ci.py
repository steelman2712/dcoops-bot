import subprocess

def run_flake8():
    try:
        subprocess.check_call(
            "flake8 --ignore=E501 --exclude=venv/,alembic/",
            shell=True
        )
    except Exception as e:
        print("flake8 failed")
        print(e)

def run_ci():
    run_flake8()

if __name__ == "__main__":
    run_ci()