FROM python:3.11-slim-bookworm as development
WORKDIR /app
RUN apt-get -y update && apt-get install -yqq dos2unix chromium chromium-driver \
    libxi6 libgconf-2-4 python3-selenium \
    tzdata git
RUN git config --global --add safe.directory /usr/src/app
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --user virtualenv
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
