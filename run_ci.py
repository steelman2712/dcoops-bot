import subprocess

failures = []


def run_black():
    try:
        subprocess.check_call(
            "black --check --exclude 'venv/*|alembic/*' .", shell=True
        )
    except Exception as e:
        print("black failed")
        failures.append("black")
        print(e)


def run_flake8():
    try:
        subprocess.check_call(
            "flake8 --ignore=E501,E402 --exclude=venv/,alembic/", shell=True
        )
    except Exception as e:
        print("flake8 failed")
        failures.append("flake8")
        print(e)


def raise_error_on_failure():
    if failures:
        raise AssertionError


def run_ci():
    run_black()
    run_flake8()
    raise_error_on_failure()


if __name__ == "__main__":
    run_ci()
