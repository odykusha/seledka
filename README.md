# SELEDKA (docker)


## Запуск тестів
для початку встановити пакет [lets](https://lets-cli.org/docs/installation/)
> `lets run seledka/tests/test_goole_passed <options>` - запуск тестів


### Інші команди докера
> `lets build` - збілдити контейнер(якщо є зміни)

> `lets pull` - зпулити актуальний контейнер

> `lets push` - запушати актуальний контейнер

> `lets flake8` - перевірка проекта на flake8

> `lets bash` - відкрити bash в середині контейнера

> `lets version` - версії google-chrome в контейнері


# SELEDKA (env)
## Втановлення залежностей
Потрібен `python3.12` виконав наступні команди
```
sudo apt-get install python3.12-venv
python3.12 -m venv env
./env/bin/python -m pip install -r requirements.txt
```


## запуск тестів
> `pytest` - всіх

> `pytest -n2` - в `2`потока

> `pytest seledka/tests/test_goole_passed` - тільки ті що в файлі

> `pytest seledka/tests/test_goole_passed -k test_search_webdriver_passed` - тільки окремий 


##
##
## Корисні бібліотеки
* [selenium](https://www.selenium.dev/documentation/webdriver/getting_started/)
* [browserstack](https://automate.browserstack.com/)
* [xdist](https://pytest-xdist.readthedocs.io/en/stable/)
* [faker](https://faker.readthedocs.io/en/latest/providers/faker.providers.address.html)
* [requests](https://docs.python-requests.org/en/latest/)
* [selenoid](https://github.com/aerokube)
* [allure](https://allurereport.org/)