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
from zeep import Client

#ips del olt traidas desde la ejecucion del archivo disparador.sh
ip_olt = '10.125.20.183'
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
        sql = text('SELECT * FROM arreglar(:ip_olt)')
        query = connection.execute(sql, {'ip_olt': ip_olt})
        ordenes = [list(row) for row in query]

        array = numpy.array(ordenes)
        result_rows, result_columns = array.shape#saber tamaño de columanas y filas del array
        
        j=0
        while j<result_rows:
            
                        
            descripcion = ordenes[j][2]
            
            #-----------------------AAA--------------------------
            if descripcion.find('aaa'):
                
                #-----------------CREAR AAA --------------------------
                imsi = str(ordenes[j][1])            
                numero_identificador = str(ordenes[j][0])
                subscriberid =str( ordenes[j][4])
                product_id = str(ordenes[j][3])
                serial_modem = ordenes[j][8]
                effectTime=now.strftime("%Y%m%d")+'000000'
                timeStampSN=now.strftime("%Y%m%d")+'0000000001010101'

                url = "http://200.44.45.149/api/ApiCrearNuevoSuscriptor?IMSI=J296692343&contactTeleNo="+numero_identificador+"&payAccount=0&productID="+product_id+"&sequenceId=0&serialNo=0&subscriberID="+subscriberid+"&serial_modem="+serial_modem

                try:
                    crear_aaa=requests.request("POST", url)
                    logging.debug(crear_aaa) 
                except:
                    logging.warning(numero_identificador+' error conexion no se ha podido crear en el AAA')   
                    
                
                #-----------------CONFIRMAR AAA --------------------------

                url = "http://200.44.45.149/api/ApiConsultarSuscriptor?subscriberId="+subscriberid

                try:
                    consulta_suscriptor=requests.request("POST", url)                
                    logging.debug(consulta_suscriptor) 
                except:
                    logging.warning(numero_identificador+' error conexion no se ha podido crear en el AAA') 


                pic=consulta_suscriptor.text

                if pic.find('Operation successfully')>-1:
                    logging.info(numero_identificador+' se ha creado exitosamente en el AAA')
                    response_aaa = 1
                else:
                    logging.warning(numero_identificador+' no se ha podido crear en el AAA')            
                    response_aaa = 0                

            #-----------------------ONT ID------------------------                    
            if descripcion.find('ont_id'):
                
                slot = ordenes[j][5]
                vlan= str(int(slot) + 200)
                puerto = ordenes[j][6]
                ont_id = ordenes[j][7]
                serial_modem = ordenes[j][8]
                lineprofile = ordenes[j][9]
                srvprofile = ordenes[j][10]
                serviceport = ordenes[j][11]
                ci  =  ordenes[j][1]

                #---------------CREAR ONT_ID
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
                devices_access.send("ont add "+puerto+" "+ont_id+" sn-auth "+serial_modem+" omci ont-lineprofile-id  "+lineprofile+"  ont-srvprofile-id "+srvprofile+" desc '"+ci+"'\n")
                time.sleep(1)
                devices_access.send("ont tr069-server-config "+puerto+" "+ont_id+" profile-id 1\n\n")
                time.sleep(1)
                devices_access.send("ont reset "+puerto+" "+ont_id+"\n")
                time.sleep(1)
                devices_access.send("quit\n")
                time.sleep(1)
                devices_access.send("quit\n")
                time.sleep(2)
                devices_access.send("quit\n")    
                output = devices_access.recv(9999999)        
                response=output.decode('ascii')
                logging.debug(response)
                cliente.close()   
            
                #-------------CONFIRMAR ONT_ID-----------------------
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
                devices_access.send("display ont info by-sn "+serial_modem+"\n")
                time.sleep(1)
                            
                time.sleep(1)
                        
                time.sleep(1)
                devices_access.send("quit\n")
                time.sleep(2)
                devices_access.send("quit\n")    
                output = devices_access.recv(9999999)        
                response=output.decode('ascii')
                logging.debug(response)
                cliente.close()

                if response.find('The required ONT does not exist')>-1:
                    logging.warning(serial_modem+' no se creo el ont_id')                
                    response_ont = 0
                else:
                    logging.info(serial_modem+' se creo el ont_id')
                    response_ont = 1

            #-----------------------SERVICESPORT-------------------                                                    
            if descripcion.find('serviceport'):
                slot = ordenes[j][5]
                vlan= str(int(slot) + 200)
                puerto = ordenes[j][6]
                ont_id = ordenes[j][7]
                serial_modem = ordenes[j][8]
                lineprofile = ordenes[j][9]
                srvprofile = ordenes[j][10]
                serviceport = ordenes[j][11]                
                c_vlan = ordenes[j][12]
                vs = ordenes[j][13]
                vb = ordenes[j][14]

                #-------------------------------------CREAR SERVICESPORT--------------------------------------                    
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
                devices_access.send("service-port "+serviceport+" vlan "+vlan+" gpon 0/"+slot+"/"+puerto+" ont "+ont_id+" gemport 11 multi-service user-vlan 10 tag-transform translate-and-add inner-vlan "+c_vlan+" inbound traffic-table index "+vs+" outbound traffic-table index "+vb+"\n")
                time.sleep(1)
                devices_access.send("mac-address max-mac-count service-port "+serviceport+" 4\n")
                time.sleep(1)
                devices_access.send("quit\n")
                time.sleep(2)
                devices_access.send("quit\n")
                time.sleep(1)     
                output = devices_access.recv(6000)        
                response=output.decode('ascii')
                logging.debug(response)    
                cliente.close()  

                #-------------------------------------CONFIRMAR SERVICESPORT--------------------------------------    
                
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
                                    
                devices_access.send("display service-port"+serviceport+"\n")
                time.sleep(1)            
                devices_access.send("quit\n")
                time.sleep(2)
                devices_access.send("quit\n")
                time.sleep(1)     
                output = devices_access.recv(6000)        
                response=output.decode('ascii')
                logging.debug(response)    
                cliente.close()  

                if response.find('Failure: Service virtual port does not exist')>-1:
                    logging.warning(serial_modem+' no se creo el servicepor')                
                    response_serviceport = 0
                else:
                    logging.info(serial_modem+' se creo el serviceport')
                    response_serviceport = 1


            #------------------------------------DEFINIR STATUS---------------------------------------

            if response_aaa==0 and response_ont==0 and response_serviceport==0:

                sql = text('UPDATE ordens SET descripcion= :descripcion,status= :status WHERE serial_modem= :serial_modem')
                query = connection.execute(sql, {'descripcion': 'error: aaa,serviceport,ont_id','status': 9,'serial_modem': serial_modem})

            elif response_aaa==1 and response_ont==0 and response_serviceport==0:
                
                sql = text('UPDATE ordens SET descripcion= :descripcion,status= :status WHERE serial_modem= :serial_modem')
                query = connection.execute(sql, {'descripcion': 'error: serviceport,ont_id','status': 9,'serial_modem': serial_modem})

            elif response_aaa==1 and response_ont==1 and response_serviceport==0:
                
                sql = text('UPDATE ordens SET descripcion= :descripcion,status= :status WHERE serial_modem= :serial_modem')
                query = connection.execute(sql, {'descripcion': 'error: serviceport','status': 9,'serial_modem': serial_modem})

            elif response_aaa==1 and response_ont==1 and response_serviceport==1:
                
                sql = text('UPDATE ordens SET status= :status WHERE serial_modem= :serial_modem')
                query = connection.execute(sql, {'status': 3,'serial_modem': serial_modem})    
            
            j+=1 

               
finally:
 
    logging.debug('fallo')



    


