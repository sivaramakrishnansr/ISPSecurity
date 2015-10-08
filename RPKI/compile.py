file_to_open=open('stats','r')
file_to_write=open('minlan','a')
for line in file_to_open:
	line=line.split(' ')
	file_to_write.write('Client->Server   - (SSL connection) -  Client connected with a successful verification of a ROA certificate with the server in '+str(line[1])+" s\n")
	file_to_write.write('Total Time seen at client for processing the request -'+ str(line[2])+' s\n')
	file_to_write.write('Total Time seen at client for processing the request and validating the RPKI -' +str(float(line[1])+float(line[2]))+" s\n")
	
