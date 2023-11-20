FROM python:3.12.0-slim

COPY . /opt/
RUN apt-get update --no-install-recommends && apt-get install -y apt-utils software-properties-common --no-install-recommends \
    && apt-get install -y `grep -v '#' /opt/selenium_env.txt | xargs` --no-install-recommends \
    && apt-get autoremove -y && apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/share/zoneinfo/Europe/Kiev /etc/localtime && locale-gen en_US.UTF-8 ru_RU.UTF-8 ru_UA.UTF-8

RUN python3.12 -m pip install --no-cache-dir -U -r  /opt/requirements.txt


#============================================
# Google Chrome https://googlechromelabs.github.io/chrome-for-testing/
# last chromedriver version: https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json
#============================================
RUN CHROME_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json | python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])") \
    && echo "Using chrome version: "$CHROME_VERSION \
    && wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chrome-linux64.zip -O /opt/google-chrome.zip \
    && unzip /opt/google-chrome.zip -d ~ \
    && mv ~/chrome-linux64 ~/chrome \
    && ln -s ~/chrome/chrome /usr/local/bin/chrome \
    && chmod +x ~/chrome \
    && rm /opt/google-chrome.zip \
    && wget --no-verbose -O /tmp/chromedriver_linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver_linux64.zip -d /opt/selenium \
    && ln -fs /opt/selenium/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && rm /tmp/chromedriver_linux64.zip


ENV DISPLAY=:0
VOLUME $HOME/.Xauthority && /tmp/.X11-unix

WORKDIR /work


RUN echo =============== installed browser ================ \
  && echo $(google-chrome --version) \
  && echo $(chromedriver --version) \
  && echo ==================================================
