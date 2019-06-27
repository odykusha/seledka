HASH_SUM = `./docker/check_enviroment_changes.sh`
SE_ENV_CONTAINER = odykusha/seledka:$(HASH_SUM)


# !!!!! parsing arguments !!!!!!!
ifeq (pull,$(firstword $(MAKECMDGOALS)))
  SEPULL_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
endif

ifeq (test,$(firstword $(MAKECMDGOALS)))
  SETEST_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
endif


build:
	@echo "==================================================================="
	@echo ">>>> [BUILD docker images]"
	@if [ -z "$$(docker images -q $(SE_ENV_CONTAINER))" ]; then \
		sh ./docker/build.sh; \
	else \
		echo ">>>> Found local container '$(SE_ENV_CONTAINER)'"; \
	fi;
	@echo ">>>> Done."


pull:
	@# [example]: make pull seledka
	@# [example]: make pull seledka:d6eb12c2
	@echo "==================================================================="
	@echo ">>>> [PULL docker images]"
	@docker login
	@echo ">>>> Please wait, i'm pulling..."

	@if [ ! -z "$(SEPULL_ARGS)" ]; then \
		docker pull odykusha/$(SEPULL_ARGS); \
		echo ">>>> Done."; \
	else \
		if [ "$$(docker pull $(SE_ENV_CONTAINER) 2> /dev/null)" != "" ]; then \
			echo ">>>> Download $(SE_ENV_CONTAINER)"; \
			echo ">>>> Done."; \
		else \
			echo "==================================================================="; \
			echo ">>>> [Not found container $(SE_ENV_CONTAINER)], use command 'make build'"; \
		fi; \
	fi;


push:
	@echo "==================================================================="
	@echo ">>>> [PUSH docker images]"
	@docker login
	docker push $(SE_ENV_CONTAINER)
	@echo ">>>> Pushed $(SE_ENV_CONTAINER) in: https://cloud.docker.com"
	@echo ">>>> Done."


test:
	@# [example]: make test -- tests/ (...)
	@echo "==================================================================="
	@echo ">>>> [RUN tests in docker]"
	@xhost +SI:localuser:root
	@if [ -z "$$(docker images -q $(SE_ENV_CONTAINER))" ]; then \
		echo ">>>> Don't found local container '$(SE_ENV_CONTAINER)', try upload from cloud..."; \
		$(MAKE) -s pull; \
	fi;
	@if [ -z "$$(docker images -q $(SE_ENV_CONTAINER))" ]; then \
		echo ">>>> Don't found in registry container '$(SE_ENV_CONTAINER)', build new container..."; \
		$(MAKE) -s build; \
	fi;
	@#$(MAKE) -s clean
	@docker run --net=host -v "$(PWD)":/work -it $(SE_ENV_CONTAINER) pytest $(SETEST_ARGS)


version:
	@# actual container version
	@echo $(SE_ENV_CONTAINER)


clean:
	@# save last 2 images, and remove all another
	@#echo "" > .pytest_cache/v/cache/lastfailed &2>/dev/null
	@find -name '*.pyc' -delete
	@python docker/remove_old_images.py odykusha/seledka


flake8:
	@# check all file in project
	@flake8
