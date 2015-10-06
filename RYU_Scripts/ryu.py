import os
os.system('sudo apt-get update')
os.system('sudo apt-get install python-pip')
os.system('sudo apt-get install python-greenlet')
os.system('sudo apt-get install msgpack-python')
os.system('sudo apt-get install python-routes')
os.system('sudo apt-get install python-webob')
os.system('sudo apt-get install python paramiko')


os.system('sudo pip install /users/satyaman/ryu_dependencies/eventlet-0.15.2-py2.py3-none-any.whl')
os.system('sudo pip install six-1.9.0-py2.py3-none-any.whl')
os.system('sudo dpkg -i python-pbr_0.8.2-0ubuntu1_all.deb')
os.system('sudo pip install netaddr-0.7.18-py2.py3-none-any.whl')
os.system('sudo pip install stevedore-1.1.0-py2.py3-none-any.whl')
os.system('sudo pip install oslo.config-1.7.0-py2.py3-none-any.whl')

os.system('python /users/satyaman/ryu/ryu-master/setup.py install')
