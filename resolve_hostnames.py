import socket
import ipaddress

def hostname_to_ip(ip_file):
	file = open(ip_file, 'r')
	ip_list = []

	for host_name in file:
		host_ip = socket.gethostbyname(host_name.strip())
		ip_list.append(host_ip)

	return ip_list