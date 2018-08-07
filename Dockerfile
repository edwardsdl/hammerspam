FROM python:3.6-slim-stretch

# Create user account
RUN useradd --create-home --system hammerspam
USER hammerspam

WORKDIR /srv/hammerspam

# Install packages
COPY --chown=hammerspam requirements.txt requirements.txt
RUN pip install --user --no-warn-script-location --requirement requirements.txt

# Copy application
COPY --chown=hammerspam app.py app.py
COPY --chown=hammerspam hammerspam hammerspam

# Run application
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]
