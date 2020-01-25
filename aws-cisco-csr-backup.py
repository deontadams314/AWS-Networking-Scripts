import paramiko
import multiprocessing as mp

class CiscoCSR():
	def __init__(self):
		#variables for the CSR device
		self.ec2_user_name = "xxx-xxxx"
		self.bastion_public_ip = "x.x.x.x"
		self.bastion_private_ip = "x.x.x.x"
		self.csr_01_private_ip = "x.x.x.x.x"
		self.pem_key = paramiko.RSAKey.from_private_key_file("x.x.x.x.x")
		self.device_list = [self.csr_01_private_ip]
		
	def backup_csr(self, device):
		try:
			#Connect to AWS Bastion host
			print('CONNECTING TO AWS HOST: {}...'.format(self.bastion_public_ip))
			bastion_client = paramiko.SSHClient()
			bastion_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			bastion_client.connect(hostname=self.bastion_public_ip, username=self.ec2_user_name, pkey=self.pem_key)
			print('CONNECTED SUCCESSFULLY!')

			#Create transport details & create the channel
			print('GETTING TRANSPORT DETAILS & CREATING THE SSH CHANNEL...')
			transport = bastion_client.get_transport()
			dest_addr = (device, 22)
			local_addr = (self.bastion_private_ip, 22)
			channel = transport.open_channel("direct-tcpip", dest_addr, local_addr, timeout=10)
			print('CHANNEL CREATED!')

			#Create new client for the CSR device and pass the channel to it as a socket
			print("CONNECTING TO CSR1: {}...".format(device))
			csr_client = paramiko.SSHClient()
			csr_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			csr_client.connect(hostname=device, username=self.ec2_user_name, pkey=self.pem_key, sock=channel)
			print("CONNECTED SUCCESSFULLY!")

			#Grab running config for the CSR and saves it to a text file
			print('GRABBING THE CURRENT RUNNING CONFIG...')
			stdin, stdout, stderr = csr_client.exec_command('show run' )
			output = stdout.readlines()
			file = open('{}-running-config.txt'.format(device), 'w')
			for line in output:
				file.write(line)
				#print(line.strip())
			file.close()
			print('[COMPLETE] CONFIG SAVED FOR HOST {} CLOSING CONNECTIONS...'.format(device))
			csr_client.close()
			print('CONNECTION CLOSED FOR: {}'.format(device))
			bastion_client.close()
			print('CONNECTION CLOSED FOR: {}'.format(self.bastion_public_ip))
			print('[###########BYE BYE###########]')

		except Exception as error:
			print("[ERROR] There was an issue see message: [{}]".format(error))

	def main(self): 
		#Function to multi process the backup of each device
		processes = []
		try:
			for host in self.device_list:
				processes.append(mp.Process(target=self.backup_csr, args=(host,)))
			#launch the process
			for p in processes:
				p.start()
			#join the forked processes into the main thread
			for p in processes:
				p.join()
		except Exception as error:
			print("[ERROR] There was an issue see message: [{}]".format(error))

if __name__ == '__main__':
	backup = CiscoCSR()
	backup.main()