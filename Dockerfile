FROM runpod/pytorch:3.10-2.0.0-117

SHELL ["/bin/bash", "-c"]

WORKDIR /

# Update and upgrade the system packages (Worker Template)
RUN apt-get update && \
    apt-get upgrade -y && apt install rustc cargo -y

# Install Python dependencies (Worker Template)
COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip wheel setuptools_rust && pip install tokenizers && \
    pip install -r /requirements.txt && \
    rm /requirements.txt

ADD . .

# Cleanup section (Worker Template)
RUN apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

CMD [ "python", "-u", "predict.py" ]