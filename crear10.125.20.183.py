import paramiko
import time
from getpass import getpass
import sys
import psycopg2
import psycopg2.extensions
import numpy
from db import conexion
from pathlib import Path
from xml.etree import ElementTree
import xmltodict
import json
import logging
from datetime import datetime as dt
import socket
import requests

now=dt.now()
name_log = './logs/aprov/'+now.strftime("%Y%m%d%H")+'.log'

nombre_pc=socket.gethostname()
remoteAddress=socket.gethostbyname(nombre_pc)


#ips del olt traidas desde la ejecucion del archivo disparador.sh
ip_olt = '10.125.20.183'
user="AprovCantv" 
password="Apr0vC@ntv#21$"


try:
    with conexion.cursor() as cur:
        
        #consulta de las ordenes en estatus null filtrado por la ip del olt
        sql = """SELECT * FROM aprov(%s);"""
        cur.execute(sql,[ip_olt])
        ordenes = cur.fetchall()
       
        array = numpy.array(ordenes)
        result_rows, result_columns = array.shape#saber tamaño de columanas y filas del array

        #-------------------------------------CREAR AAA--------------------------------------
        j=0
        while j<result_rows:
            imsi = ordenes[j][1]
            numero_identificador = ordenes[j][0]
            subscriberid = ordenes[j][3]
            product_id = ordenes[j][2]

            effectTime=now.strftime("%Y%m%d")+'000000'
            timeStampSN=now.strftime("%Y%m%d")+'0000000001010101'

            url="http://picpw10:8801/mule/services/AP900CrearNuevoSuscriptorAba?wsdl"
            xml="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:mul="http://MULECrearNuevoSuscriptorAba/" xmlns:mul1="http://MULECrearNuevoSuscriptorAba">
            <soapenv:Header/>
            <soapenv:Body>
            <mul:CrearNuevoSuscriptor>
                <!--Optional:-->
                    <mul:arg0>
                            <mul1:IDCLIENTEPIC>GPON</mul1:IDCLIENTEPIC>
                            <mul1:IMSI>"""+imsi+"""</mul1:IMSI>
                            <mul1:chargingType>1</mul1:chargingType>
                            <mul1:contactTeleNo>"""+numero_identificador+"""</mul1:contactTeleNo>
                            <mul1:effectTime>"""+effectTime+"""</mul1:effectTime>
                            <mul1:homeAreaID>ABA</mul1:homeAreaID>
                            <mul1:maxSessNumber>14</mul1:maxSessNumber>
                            <mul1:payAccount>0</mul1:payAccount>
                            <mul1:permittedANTYpe>3</mul1:permittedANTYpe>
                            <mul1:productID>"""+product_id+"""</mul1:productID>
                            <mul1:remoteAddress>"""+remoteAddress+"""</mul1:remoteAddress>
                            <mul1:sequenceId>0</mul1:sequenceId>
                            <mul1:serialNo>0</mul1:serialNo>
                            <mul1:subscriberID>"""+subscriberid+"""</mul1:subscriberID>
                            <mul1:timeStampSN>"""+timeStampSN+"""</mul1:timeStampSN>
                    </mul:arg0>
                </mul:CrearNuevoSuscriptor>
                </soapenv:Body>
            </soapenv:Envelope>"""

            try:
                consulta_suscriptor=requests.post(url,data=xml,timeout=50)
                logging.debug(consulta_suscriptor) 
            except:
                logging.warning(numero_identificador+' no se ha podido crear en el AAA')   
                
            pic=consulta_suscriptor.text

            if pic.find('Operation successfully')>-1:
                logging.info(numero_identificador+' se ha creado exitosamente en el AAA')               
            elif pic.find('already exists')>-1:
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
            
            query = "UPDATE ordens SET descripcion=%s,status=%s WHERE serial_modem=%s"
            cur.execute(query,['error: CONFIRMACION',8,serial_modem])
            
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
    conexion.close()



    


