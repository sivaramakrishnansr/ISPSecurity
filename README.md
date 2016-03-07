<h1>Setup</h1>

1) graph_to_mininet.py

Screipt is used to convert GraphML file into a mininet topology file. Topology Zoo provides several topologies in the GrpahML form. You can find the different topologies here.

Input

python graph_to_mininet.py -f path_to_graphml_file

2) mininet_to_deter.py

Script is used to convert the mininet file obtained in the previous version to NS file. Deterlab accepts this NS file.

3) list_of_cities

A file generated in the Setup foldler which maps individual ASN to an unique number.
To access ASN Albama, look up for the number allocated in list_of_cities. For example, if Alabama is allocated 2,you could access Alabama,by

ssh i2.experiment_name.project_name

Note:
Each link between ASNs contains an OpenVSwitch which is used for the traffic_query and traffic_filter commands. To access this OpenVSwitch,

ssh i{city_1_number}a{city_2_number}.experiment_name.project_name

where city_1_number < city_2_number (These numbers are accesed using the list_of_cities file)

4)connectivity_check.py

This script is used to check if all the nodes which are setup in the experiment are available. Deterlab takes a few minutes to set up containerised experiments.


5) Setting up the controller

Installl the dependencies
sudo python ryu_dependnties/install.py

Install RYU
cd ryu/ryu
sudo python setup.py install

Run controller
cd ryu/ryu/app/
sudo ryu-manager ofctl_rest.py --ofp-list-host {ip_of_controller}

Install Apache
sudo apt-get install apache2 php5

sudo cp -r apache_files/* /var/www/html

5)switch_setup.py

Script is used to install OpenvSwitch and Quagga on nodes. Make sure that the controller is running. You could access the controller,
ssh controller.experiment_name.project_name

python setup.py controller_ip

6)Accesing the SENSS server

ssh user_name@users.deterlab.net -L 8118:controller.experiment_name.project_name.isi.deterlab.net:80

To access the Client GUI:-
http://localhost:8181/direct_floods_form.php

To access the Server GUI:-
http://localhost:8181/index.php

7)Server GUI

Add switch

This is sued to add a new OpenvSwitch
http://localhost:8181/add_switch_form.php

IP of Switch - IP address of the switch
Name of the Switch - Used for logging purpose
Controller IP
Controller Port


Remove Switch
This is used to remove an existing Openvswitch
http://localhost:8118/remove_switch_form.php

IP of switch


