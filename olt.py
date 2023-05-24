import paramiko
import time
import sys
from getpass import getpass
import requests

class olt:


    def dataLogin():
        user="AprovCantv" 
        password="Apr0vC@ntv#21$"
        data=[user,password]
        return data

    def crear(ip_olt,slot,puerto,ont_id,serial_modem,lineprofile,srvprofile,descripcion,serviceport,vlan,c_vlan,v_up,v_down):
        try:
            #instanciar cliente ssh
            cliente = paramiko.SSHClient()
            cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #conexion ssh
            cliente.connect(hostname=ip_olt,username=user,password=password,timeout=40)
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
            devices_access.send("interface gpon 0/"+slot+"\n")
            time.sleep(1)
            #GUARDAR ONT
            devices_access.send("ont add "+puerto+" "+ont_id+" sn-auth "+serial_modem+" omci ont-lineprofile-id  "+lineprofile+"  ont-srvprofile-id "+srvprofile+" desc '"+descripcion+"'\n")
            time.sleep(1)
            #devices_access.send("ont port native-vlan "+puerto+" "+ont_id+" eth 1 vlan 10 priority 0\n")
            #time.sleep(1)
            #añasir tr69
            #devices_access.send("ont ipconfig "+puerto+" "+ont_id+" dhcp vlan "+inner_vlan+" priority 6\n\n")
            #time.sleep(1)
            devices_access.send("ont tr069-server-config "+puerto+" "+ont_id+" profile-id 1\n\n")
            time.sleep(1)
            devices_access.send("ont reset "+puerto+" "+ont_id+"\n")
            time.sleep(1)
            devices_access.send("quit\n")
            #GUARDAR SERVICEPORT
            time.sleep(1)
            devices_access.send("service-port "+serviceport+" vlan "+vlan+" gpon 0/"+slot+"/"+puerto+" ont "+ont_id+" gemport "+gemport+" multi-service user-vlan 10 tag-transform translate-and-add inner-vlan "+c_vlan+" inbound traffic-table index "+v_up+" outbound traffic-table index "+v_down+"\n")
            time.sleep(1)
            devices_access.send("mac-address max-mac-count service-port "+serviceport+" 4\n")
            time.sleep(1)
            devices_access.send("quit\n")
            time.sleep(2)
            devices_access.send("quit\n")


            time.sleep(1)
            output = devices_access.recv(6000)        
            response=output.decode('ascii')
            
            cliente.close()
        
            if response.find('Number of ONTs that can be added: 1, success: 1')>-1:
                print('exitoso')
            elif response.find('Failure: SN already exists')>-1:
                print('el serial ya existe en el olt')    
            elif response.find('The ONT ID has already existed')>-1:
                print('error de sincronizacion con el puerto')
            else:
                print("error")    
    
        except:
            print("error")
    
    def eliminar(ip_olt,serial,serviceport,slot,pto):
        user="AprovCantv" 
        password="Apr0vC@ntv#21$"

        try:
            #instanciar cliente ssh
            cliente = paramiko.SSHClient()
            cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #conexion ssh
            cliente.connect(hostname=ip_olt,username=user,password=password)
            #bloque del comando
            devices_access = cliente.invoke_shell()
            time.sleep(1)
            devices_access.send("enable\n")
            time.sleep(1)
            devices_access.send("conf\n")
            time.sleep(1)
            devices_access.send("undo smart\n")
            time.sleep(1)
            devices_access.send("undo interactive\n")
            time.sleep(1)
            devices_access.send("undo service-port "+serviceport+"\n")
            time.sleep(1)
            devices_access.send("\n")
            time.sleep(1)
            devices_access.send("interface gpon 0/"+slot+"\n")
            time.sleep(1)
            devices_access.send("ont delete "+pto+" "+ontid+"\n\n")
            time.sleep(1)
            devices_access.send("quit\n")
            time.sleep(1)
            devices_access.send("quit\n")
            time.sleep(1)
            devices_access.send("quit\n")
            time.sleep(5)
            output = devices_access.recv(35000)
            print(output.decode('ascii'))

            cliente.close()
        except:
            
            URL="http://200.44.45.149/api/EliminarOlt?ip_olt="+ip_olt+"&slot="+slot+"&puerto="+pto+"&ont_id="+ontid+"1&serviceport="+serviceport
            peticion=requests.get(URL)
            print(peticion.text) 

    
    def consultarSerial():       
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
            print(output.decode('ascii'))
            cliente.close()
        
        except:
            URL="http://200.44.45.149/api/consultaOlt?serial_modem="+serial+"&olt="+ip_olt
            peticion=requests.get(URL)

            if peticion.text=="1":
                print("existe en el olt")
            else:
                print("no existe en el olt")    