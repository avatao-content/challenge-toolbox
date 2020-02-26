FROM docker.io/centos:7

ARG PYTHON3_PKG=python36
COPY etc/ /etc/
RUN yum -y install epel-release \
    && yum -y install \
        ${PYTHON3_PKG}-devel \
        ${PYTHON3_PKG}-setuptools \
        ${PYTHON3_PKG}-pip \
        docker-ce-cli \
        git \
        google-cloud-sdk \
        unzip \
    && yum clean all

ARG PACKER_DOWNLOAD_URL="https://releases.hashicorp.com/packer/1.3.3/packer_1.3.3_linux_amd64.zip"
ARG PACKER_SHA256="2e3ea8f366d676d6572ead7e0c773158dfea0aed9c6a740c669d447bcb48d65f"
RUN curl -L -o /tmp/packer.zip "${PACKER_DOWNLOAD_URL}" \
    && echo "${PACKER_SHA256} /tmp/packer.zip" | sha256sum -c - \
    && unzip -o -j -d /usr/local/bin /tmp/packer.zip packer \
    && rm -f /tmp/packer.zip

COPY toolbox/ /opt/avatao/toolbox/
COPY *.py *.sh requirements.txt /opt/avatao/
WORKDIR /opt/avatao/
RUN pip3 install -r requirements.txt

ENV PATH="/opt/avatao:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["entrypoint.sh"]
CMD ["deploy.py"]
