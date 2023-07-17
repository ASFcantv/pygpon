import paramiko
import time
from getpass import getpass
import sys
import numpy
from pathlib import Path
from xml.etree import ElementTree
import xmltodict
import json
import logging
from datetime import datetime as dt
import socket
import requests
from db import engine
from sqlalchemy import text

#ips del olt traidas desde la ejecucion del archivo disparador.sh
ip_olt = '10.125.139.143'
user="AprovCantv" 
password="Apr0vC@ntv#21$"

now=dt.now()
name_log = './logs/aprov/'+now.strftime("%Y%m%d%H")+'_'+ip_olt+'.log'
logging.basicConfig(filename=name_log, level=logging.DEBUG)

nombre_pc=socket.gethostname()
remoteAddress=socket.gethostbyname(nombre_pc)

try:
    with engine.connect() as connection:
        
        #consulta de las ordenes en estatus null filtrado por la ip del olt
        sql = text('SELECT * FROM aprov(:ip_olt)')
        query = connection.execute(sql, {'ip_olt': ip_olt})
        ordenes = [list(row) for row in query]

        if len(ordenes)==2 :
            array = numpy.array(ordenes)
            result_rows, result_columns = array.shape#saber tamaño de columanas y filas del array

            #-------------------------------------CREAR AAA--------------------------------------
            j=0
            while j<result_rows:
                imsi = str(ordenes[j][1])            
                numero_identificador = str(ordenes[j][0])
                subscriberid =str( ordenes[j][3])
                product_id = str(ordenes[j][2])
                serial_modem = ordenes[j][7]
                effectTime=now.strftime("%Y%m%d")+'000000'
                timeStampSN=now.strftime("%Y%m%d")+'0000000001010101'
        
                url = "http://200.44.45.149/api/ApiCrearNuevoSuscriptor?IMSI=J296692343&contactTeleNo="+numero_identificador+"&payAccount=0&productID="+product_id+"&sequenceId=0&serialNo=0&subscriberID="+subscriberid+"&serial_modem="+serial_modem

                try:
                    crear_aaa=requests.request("POST", url)
                    logging.debug(crear_aaa) 
                except:
                    logging.warning(numero_identificador+' error conexion no se ha podido crear en el AAA')   
                    
                pic=crear_aaa.text

                if pic.find('exitoso')>-1:
                    logging.info(numero_identificador+' se ha creado exitosamente en el AAA')               
                elif pic.find('ya existe')>-1:
                    logging.warning(numero_identificador+' se ha creado previamente en el AAA por favor verificar')
                else:
                    logging.warning(numero_identificador+' no se ha podido crear en el AAA')
                j+=1
            
            #--------------------------------------------CREAR ONT_ID --------------------------

            i=0
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
            while i<result_rows:
                
                slot = ordenes[i][4]
                vlan= str(int(slot) + 200)
                puerto = ordenes[i][5]
                ont_id = ordenes[i][6]
                serial_modem = ordenes[i][7]
                lineprofile = ordenes[i][8]
                srvprofile = ordenes[i][9]
                descripcion = ordenes[i][10]
            
                
                time.sleep(1)
                devices_access.send("interface gpon 0/"+slot+"\n")
                time.sleep(1)
                #GUARDAR ONT
                devices_access.send("ont add "+puerto+" "+ont_id+" sn-auth "+serial_modem+" omci ont-lineprofile-id  "+lineprofile+"  ont-srvprofile-id "+srvprofile+" desc '"+descripcion+"'\n")
                time.sleep(1)
                devices_access.send("ont tr069-server-config "+puerto+" "+ont_id+" profile-id 1\n\n")
                time.sleep(1)
                devices_access.send("ont reset "+puerto+" "+ont_id+"\n")
                time.sleep(1)
                devices_access.send("quit\n")            

                time.sleep(1)
                
                i+=1
            time.sleep(1)
            devices_access.send("quit\n")
            time.sleep(2)
            devices_access.send("quit\n")    
            output = devices_access.recv(9999999)        
            response=output.decode('ascii')
            logging.debug(response)
            cliente.close()
            
            
            #-----------------CREAR SERVICEPORT --------------------------
            
            x=0
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
            while x<result_rows: 

                slot = ordenes[x][4]
                vlan= str(int(slot) + 200)
                puerto = ordenes[x][5]
                ont_id = ordenes[x][6]
                serial_modem = ordenes[x][7]
                lineprofile = ordenes[x][8]
                srvprofile = ordenes[x][9]
                serviceport = ordenes[x][10]
                descripcion = ordenes[x][1]
                c_vlan = ordenes[x][11]
                vs = ordenes[x][12]
                vb = ordenes[x][13]
                        
                
                devices_access.send("service-port "+serviceport+" vlan "+vlan+" gpon 0/"+slot+"/"+puerto+" ont "+ont_id+" gemport 11 multi-service user-vlan 10 tag-transform translate-and-add inner-vlan "+c_vlan+" inbound traffic-table index "+vs+" outbound traffic-table index "+vb+"\n")
                time.sleep(1)
                devices_access.send("mac-address max-mac-count service-port "+serviceport+" 4\n")
                time.sleep(1)
                        
                sql = text('UPDATE ordens SET descripcion= :descripcion,status= :status WHERE serial_modem= :serial_modem')
                query = connection.execute(sql, {'descripcion': descripcion,'status': 8,'serial_modem': serial_modem})
                
                x+=1 

            devices_access.send("quit\n")
            time.sleep(2)
            devices_access.send("quit\n")
            time.sleep(1)     
            output = devices_access.recv(6000)        
            response=output.decode('ascii')
            logging.debug(response)    
            cliente.close()                
finally:
 
    logging.debug('fallo')



    


