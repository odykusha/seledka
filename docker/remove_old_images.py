
import os
import sys


SAVE_LAST_CONTAINER = 2


try:
    sys.argv[1]
except IndexError:
    print('not found arguments: odykusha/seledka')
    exit(1)


docker_images = os.popen("docker images | grep %s" % sys.argv[1]).read()

for item in docker_images.split('\n')[SAVE_LAST_CONTAINER:-1]:
    image_line = item.split('   ')
    if image_line[1] == 'latest':
        continue
    else:
        os.popen("docker rmi -f %s" % image_line[2])
        print('delete %s' % image_line[2])
