FROM python:3.11-slim-bookworm as development
WORKDIR /app
RUN apt-get -y update && apt-get install -yqq dos2unix \
    libxi6 libgconf-2-4 \
    tzdata git gcc
RUN apt-get install -y locales && \
    sed -i -e 's/# en_GB.UTF-8 UTF-8/en_GB.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    locale-gen
ENV LANG en_GB.UTF-8
ENV LC_ALL en_GB.UTF-8    
RUN git config --global --add safe.directory /app
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --user virtualenv
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
