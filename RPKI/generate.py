import os
file_name=open("final/complete_list","r")
dict={}
for line in file_name:
	line_split=line.split('|')
	if line_split[0].strip() in dict:
		dict[line_split[0].strip()].append(line)
	else:
		dict[line_split[0].strip()]=[]

print len(dict)
count=11
for key,value in dict.iteritems():
	ip_addr="      "
	issuer=""
	for item in value:
		item=item.split('|')
		ip_addr=ip_addr+str(item[1]).strip()+","
		issuer=str(item[2]).strip()
	ip_addr=ip_addr[:-1]
	as_name=str(key).strip()
	#count=count + 1

	
	config_file=open('openssl-server.cnf','w')
	config_file.write("HOME            = .\n")
	config_file.write("RANDFILE        = $ENV::HOME/.rnd\n")

	config_file.write("####################################################################\n")
	config_file.write("[ req ]\n")
	config_file.write("default_bits        = 2048\n")
	config_file.write("default_keyfile     = serverkey.pem\n")
	config_file.write("distinguished_name  = server_distinguished_name\n")
	config_file.write("req_extensions      = server_req_extensions\n")
	config_file.write("string_mask         = utf8only\n")

	config_file.write("####################################################################\n")
	config_file.write("[ server_distinguished_name ]\n")
	config_file.write("countryName         = Country Name (2 letter code)\n")
	config_file.write("countryName_default     = US\n")

	config_file.write("stateOrProvinceName     = State or Province Name (full name)\n")
	config_file.write("stateOrProvinceName_default = CA\n")

	config_file.write("localityName            = Locality Name (eg, city)\n")
	config_file.write("localityName_default        = Los Angeles\n")

	config_file.write("organizationName         = Organization Name (eg, company)\n")
	config_file.write("organizationName_default    = "+str(issuer)+", Limited\n")

	config_file.write("commonName          = Common Name (e.g. server FQDN or YOUR name)\n")
	config_file.write("commonName_default      = Test CA\n")

	config_file.write("emailAddress            = Email Address\n")
	config_file.write("emailAddress_default        = satyaman@usc.edu\n")

	config_file.write("####################################################################\n")
	config_file.write("[ server_req_extensions ]\n")

	config_file.write("subjectKeyIdentifier        = hash\n")
	config_file.write("basicConstraints        = CA:FALSE\n")
	config_file.write("keyUsage            = digitalSignature, keyEncipherment\n")
	config_file.write("nsComment = \"NSL-ISI Generated Certificate\"\n")
	config_file.write("nsComment=AS:"+as_name+"\n")
	config_file.write("1.2.3.4=critical,ASN1:UTF8String:"+ip_addr+"\n")

	config_file.close()
	temp_string="openssl req -config openssl-server.cnf -newkey rsa:2048 -sha256 -subj \"/C=US/ST=California/L=Los Angeles/O=NSL/CN=satyaman@usc.edu\" -out servercert"+str(count)+".csr  -passout pass:nslisi -outform PEM"
	os.system(temp_string)

	os.system("rm index.txt")
	os.system("rm serial.txt")
	os.system("touch index.txt")

	#temp_string="echo '07' > serial.txt"
	temp_string="echo '"+str(count)+"' > serial.txt"
	os.system(temp_string)

	#FIX THHIS
	temp_string="openssl ca -batch -config openssl-ca.cnf -policy signing_policy -extensions signing_req -out "+str(as_name)+".pem -passin pass:nslisi -infiles servercert"+str(count)+".csr"
	os.system(temp_string)

	temp_string="mkdir Certificates2/"+str(as_name)
	os.system(temp_string)

	temp_string="cp "+str(as_name)+".pem Certificates2/"+str(as_name)
	os.system(temp_string)

	temp_string="rm "+str(as_name)+".pem"
	os.system(temp_string)
	break
