# SELEDKA (docker)


## Запуск тестов
> `make se-test -- -- core/tests/test_goole_passed <options>` - запуск тестов в докер контейнере


### Другие команды докера
> `make se-build` - сбилдить контейнер

> `make se-push` - запушать актуальный контейнер

> `make se-pull` - спулить актуальный контейнер

> `make se-version` - текущий хеш конейнера

> `make se-remove-old-images` - удалить старые контейнеры(кроме последних 3х)


# SELEDKA (env)
## Установка зависимостей
Нужен `python3.7` выполнив следующие команды
```
sudo apt-get install python3.7-venv
python3.7 -m venv env
./env/bin/python -m pip install -r requirements.txt
```


## запуск тестов
> `pytest` - всех тестов

> `pytest -n2` - в `2`потока

> `pytest core/tests/test_goole_passed` - только всех что в файле

> `pytest core/tests/test_goole_passed -k test_search_webdriver_passed` - только определенного 


##
##
## Полезные библиотеки
* [webdriver](https://selenium-python.readthedocs.io/api.html)
* [faker](https://faker.readthedocs.io/en/latest/providers/faker.providers.address.html)
* [selenoid](https://github.com/aerokube)
* [requests](http://docs.python-requests.org/en/master/)


