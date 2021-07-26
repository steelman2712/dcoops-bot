FROM python:3.8

COPY requirements.txt requirements_from_github.txt /tmp/
RUN pip install -r /tmp/requirements.txt


ADD https://api.github.com/repos/steelman2712/site-utils/git/refs/heads/main version.json
RUN pip install -r /tmp/requirements_from_github.txt

RUN useradd --create-home backenduser
WORKDIR /home/backenduser
USER backenduser

COPY . .

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]