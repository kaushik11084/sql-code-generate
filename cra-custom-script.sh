#Uninstall default python3.6 and install 3.8 or 3.9 or 3.10 etc depending on version required with pip22+
yum remove -yq python3.6
yum install -yq python3.8 python3-pip
unlink /usr/bin/python3
unlink /usr/bin/pip3
ln -s /usr/bin/python3.8 /usr/bin/python3
ln -s /usr/bin/pip3.8 /usr/bin/pip3
python3 -m pip install --upgrade pip
