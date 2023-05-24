import requests
import paramiko
import time
import sys
from getpass import getpass

ip_olt=input("introducir ip de olt : ")
serial=input("introducir serial del ont : ")
user="AprovCantv" 
password="Apr0vC@ntv#21$"

try:
    
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #conexion ssh
    cliente.connect(hostname=ip_olt,username=user,password=password)
    #bloque del comando
    devices_access = cliente.invoke_shell()
    devices_access.send("enable\n")
    time.sleep(1)
    devices_access.send("config\n")
    time.sleep(1)
    devices_access.send("undo smart\n")
    time.sleep(1)
    devices_access.send("undo interactive\n")
    time.sleep(1)
    devices_access.send("display ont info by-sn "+serial+" \n")
    time.sleep(1)
    devices_access.send("\n quit \n")
    time.sleep(1)
    devices_access.send("quit\n")

    time.sleep(1)
    output = devices_access.recv(3500)
    print(output)
    cliente.close()

except:
    URL="http://200.44.45.149/api/consultaOlt?serial_modem="+serial+"&olt="+ip_olt
    peticion=requests.get(URL)

    print(peticion.text)
