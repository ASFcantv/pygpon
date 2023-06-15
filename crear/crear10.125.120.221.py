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
from datetime import datetime as dt
import socket
import logging
import requests

now=dt.now()
name_log = './logs/aprov/'+now.strftime("%Y%m%d%H")+'.log'
logging.basicConfig(filename=name_log, level=logging.DEBUG)
nombre_pc=socket.gethostname()
remoteAddress=socket.gethostbyname(nombre_pc)


#ips del olt traidas desde la ejecucion del archivo disparador.sh
ip_olt = '10.125.120.221'
user="AprovCantv" 
password="Apr0vC@ntv#21$"




try:
    with conexion.cursor() as cur:
        
        #consulta de las ordenes en estatus null filtrado por la ip del olt
        sql = """SELECT o.numero_identificador,o.documento
        ,a."productID",a.subscriberid
        ,c.slot,c.puerto,c.ont_id,c.serial_modem,c.lineprofile,c.srvprofile,c.serviceport,c.c_vlan,c.vsubida,c.vbajada
        FROM ordens o
        JOIN comands c ON c.serial_modem=o.serial_modem
        JOIN aaa_users a ON a."contactTeleNo"=o.numero_identificador
        JOIN tao_details td ON o.id_tao=td.id_tao
        JOIN olts ol ON ol.id=td.olt_id
        WHERE o.status IS NULL  AND ol.ip_olt=%s ;
        """

        cur.execute(sql,[ip_olt])
        ordenes = cur.fetchall()        
        array = numpy.array(ordenes)
        result_rows, result_columns = array.shape#saber tamaño de columanas y filas del array

        #------------------------------------------APROVISIONAR EN AAA ------------------------------------------------------------

        j=0
        while j<result_rows:
            imsi = ordenes[0][1]
            numero_identificador = ordenes[0][0]
            subscriberid = ordenes[0][3]
            product_id = ordenes[0][2]

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
            except:
                logging.warning(subscriberid + ' fallo en ejecucion')

            pic=consulta_suscriptor.text

            if pic.find('Operation successfully')>-1:
                logging.info(subscriberid+' / '+numero_identificador+' exitoso')
            elif pic.find('already exists')>-1:
                logging.warning(subscriberid+' / '+numero_identificador+ ' ya existe en el AAA') 
            else:
                logging.warning(subscriberid+' / '+numero_identificador+ ' fallo al crear el AAA')
            j+=1

        
        
        #----------------------------------------------APROVISIONAR OLT CREAR ONT_ID ----------------------------------------------
        
        i=0
        #instanciar cliente ssh
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #conexion ssh
        cliente.connect(hostname=ip_olt,username=user,password=password,timeout=140)
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
            
            slot = ordenes[0][4]
            vlan= str(int(slot) + 200)
            puerto = ordenes[0][5]
            ont_id = ordenes[0][6]
            serial_modem = ordenes[0][7]
            lineprofile = ordenes[0][8]
            srvprofile = ordenes[0][9]
            descripcion = ordenes[0][10]

           
            
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
        output = devices_access.recv(6000)        
        response=output.decode('ascii')        
        cliente.close()

        #----------------------------------------------APROVISIONAR OLT CREAR SERVICEPORT ----------------------------------------------

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

            slot = ordenes[0][4]
            vlan= str(int(slot) + 200)
            puerto = ordenes[0][5]
            ont_id = ordenes[0][6]
            serial_modem = ordenes[0][7]
            lineprofile = ordenes[0][8]
            srvprofile = ordenes[0][9]
            serviceport = ordenes[0][10]
            descripcion = ordenes[0][1]
            c_vlan = ordenes[0][11]
            vs = ordenes[0][12]
            vb = ordenes[0][13]
           
           
           
            
            devices_access.send("service-port "+serviceport+" vlan "+vlan+" gpon 0/"+slot+"/"+puerto+" ont "+ont_id+" gemport 11 multi-service user-vlan 10 tag-transform translate-and-add inner-vlan "+c_vlan+" inbound traffic-table index "+vs+" outbound traffic-table index "+vb+"\n")
            time.sleep(1)
            devices_access.send("mac-address max-mac-count service-port "+serviceport+" 4\n")
            time.sleep(1)
            
            
            x+=1 

        devices_access.send("quit\n")
        time.sleep(2)
        devices_access.send("quit\n")
        time.sleep(1)     
        output = devices_access.recv(6000)        
        response=output.decode('ascii')    
        cliente.close()         
finally:
    conexion.close()



    


