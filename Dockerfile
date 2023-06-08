FROM python:3.10.11-slim-buster 
RUN apt -y update && apt -y install wget gnupg2 xvfb libxi6 libgconf-2-4 default-libmysqlclient-dev python-dev
RUN apt-get -y install default-mysql-server default-mysql-client
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub |  apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' && apt update && apt -y install google-chrome-stable
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
WORKDIR /code
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver
COPY . /code
# команда, выполняемая при запуске контейнера
CMD ["python", "ya-parser.py"]
#CMD /bin/bash