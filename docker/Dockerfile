FROM ubuntu:bionic

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN=true

COPY . /opt/
RUN apt-get update && apt-get install -y apt-utils && \
    apt-get install -y `grep -v '#' /opt/selenium.txt | xargs` && \
    rm -rf /var/lib/apt/lists/*

ADD https://bootstrap.pypa.io/get-pip.py /opt/get-pip.py
RUN python3.7 /opt/get-pip.py


RUN ln -sf /usr/share/zoneinfo/Europe/Kiev /etc/localtime && locale-gen en_US.UTF-8 ru_RU.UTF-8 ru_UA.UTF-8

RUN python3.7 -m pip install -U -r /opt/requirements.txt


#============================================
# Google Chrome
#============================================
ARG CHROME_VERSION="google-chrome-stable"
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install \
    ${CHROME_VERSION:-google-chrome-stable} \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*


#============================================
# ChromeDriver
#============================================
RUN CHROME_VERSION=$( google-chrome --version | cut -d " " -f 3 | cut -d "." -f 1 ) \
    && CHROME_DRIVER_DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE" \
    && CHROME_DRIVER_VERSION=$(if [ ! -z $CHROME_VERSION ]; then echo $(wget -qO- "${CHROME_DRIVER_DOWNLOAD_URL}_${CHROME_VERSION}"); else echo $(wget -qO- $CHROME_DRIVER_DOWNLOAD_URL); fi) \
    && echo "Using chromedriver version: "$CHROME_DRIVER_VERSION \
    && wget --no-verbose -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver_linux64.zip -d /opt/selenium \
    && ln -fs /opt/selenium/chromedriver /usr/bin/chromedriver


#============================================
# Firefox
#============================================
ARG FIREFOX_VERSION=latest
RUN FIREFOX_DOWNLOAD_URL=$(if [ $FIREFOX_VERSION = "latest" ] || [ $FIREFOX_VERSION = "nightly-latest" ] || [ $FIREFOX_VERSION = "devedition-latest" ]; then echo "https://download.mozilla.org/?product=firefox-$FIREFOX_VERSION-ssl&os=linux64&lang=en-US"; else echo "https://download-installer.cdn.mozilla.net/pub/firefox/releases/$FIREFOX_VERSION/linux-$(uname -m)/en-US/firefox-$FIREFOX_VERSION.tar.bz2"; fi) \
  && apt-get update -qqy \
  && apt-get -qqy --no-install-recommends install firefox \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
  && wget --no-verbose -O /tmp/firefox.tar.bz2 $FIREFOX_DOWNLOAD_URL \
  && apt-get -y purge firefox \
  && rm -rf /opt/firefox \
  && tar -C /opt -xjf /tmp/firefox.tar.bz2 \
  && rm /tmp/firefox.tar.bz2 \
  && ln -fs /opt/firefox/firefox /usr/bin/firefox


#============================================
# GeckoDriver
#============================================
ARG GECKODRIVER_VERSION=latest
RUN GK_VERSION=$(if [ ${GECKODRIVER_VERSION:-latest} = "latest" ]; then echo "0.24.0"; else echo $GECKODRIVER_VERSION; fi) \
  && echo "Using GeckoDriver version: "$GK_VERSION \
  && wget --no-verbose -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v$GK_VERSION/geckodriver-v$GK_VERSION-linux64.tar.gz \
  && rm -rf /opt/geckodriver \
  && tar -C /opt -zxf /tmp/geckodriver.tar.gz \
  && rm /tmp/geckodriver.tar.gz \
  && chmod 755 /opt/geckodriver \
  && ln -fs /opt/geckodriver /usr/bin/geckodriver


#============================================
# Opera
#============================================
ARG OPERA_VERSION="60.0.3255.95"
RUN wget --no-verbose -O /opt/opera-stable_${OPERA_VERSION}_amd64.deb https://ftp.opera.com/pub/opera/desktop/$OPERA_VERSION/linux/opera-stable_${OPERA_VERSION}_amd64.deb \
  && dpkg -i /opt/opera-stable_${OPERA_VERSION}_amd64.deb


#============================================
# OperaDriver
#============================================
ARG OPERA_DRIVER_VERSION="v.2.45"
RUN wget --no-verbose -O /tmp/operadriver_linux64.zip https://github.com/operasoftware/operachromiumdriver/releases/download/$OPERA_DRIVER_VERSION/operadriver_linux64.zip \
  && unzip /tmp/operadriver_linux64.zip -d /opt/opera \
  && chmod +x /opt/opera/operadriver_linux64/operadriver \
  && ln -fs /opt/opera/operadriver_linux64/operadriver /usr/bin/operadriver


ENV DISPLAY=:0
VOLUME $HOME/.Xauthority && /tmp/.X11-unix

WORKDIR /work
ENTRYPOINT ["/work/docker/entrypoint.sh"]


RUN echo =============== installed browser ================ \
  && echo $(google-chrome --version) \
  && echo $(chromedriver --version) \
  && echo $(firefox --version) \
  && echo $(geckodriver --version | head -n 1) \
  && echo Opera $(opera --version) \
  && echo $(operadriver --version) \
  && echo ==================================================
