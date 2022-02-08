FROM docker.io/centos:7

ARG PYTHON3_PKG=python36
COPY etc/ /etc/
RUN yum -y install epel-release \
    && yum -y install \
        ${PYTHON3_PKG}-devel \
        ${PYTHON3_PKG}-setuptools \
        #${PYTHON3_PKG}-pip \
        docker-ce-cli \
        git \
        google-cloud-sdk \
        make \
        unzip \
    && yum clean all

COPY toolbox/ /opt/avatao/toolbox/
COPY *.py *.sh requirements.txt /opt/avatao/
WORKDIR /opt/avatao/
RUN python3 -m pip install -U pip
RUN pip3 install -r requirements.txt

ENV PATH="/opt/avatao:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["entrypoint.sh"]
CMD ["deploy.py"]
