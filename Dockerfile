# Pull python base image
FROM python:3.10-slim

# install the requirements from the requirements.txt file via git
RUN apt-get update && apt-get -y install libpq-dev gcc && apt-get install git postgresql-client -y --no-install-recommends


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installing requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -U pip wheel setuptools && pip install -r /tmp/requirements.txt && pip install pylint-django==2.3.0


# Copy Project to the container
RUN mkdir -p /fyle-qbd-api
COPY . /fyle-qbd-api/
WORKDIR /fyle-qbd-api

# Do linting checks
RUN pylint --load-plugins pylint_django --rcfile=.pylintrc **/**.py

#================================================================
# Set default GID if not provided during build
#================================================================
ARG SERVICE_GID=1001

#================================================================
# Setup non-root user and permissions
#================================================================
RUN groupadd -r -g ${SERVICE_GID} qbd_api_service && \
    useradd -r -g qbd_api_service qbd_api_user && \
    chown -R qbd_api_user:qbd_api_service /fyle-qbd-api

# Switch to non-root user
USER qbd_api_user

# Expose development port
EXPOSE 8000

# Run development server
CMD /bin/bash run.sh
