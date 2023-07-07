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
from db import engine
from sqlalchemy import text

now=dt.now()
name_log = './logs/aprov/'+now.strftime("%Y%m%d%H")+'.log'

nombre_pc=socket.gethostname()
remoteAddress=socket.gethostbyname(nombre_pc)


#ips del olt traidas desde la ejecucion del archivo disparador.sh
ip_olt = '10.122.173.76'
user="AprovCantv" 
password="Apr0vC@ntv#21$"


try:
   with engine.connect() as connection:
        
        #consulta de las ordenes en estatus null filtrado por la ip del olt
        sql = text('SELECT * FROM confirmacion(:ip_olt)')
        query = connection.execute(sql, {'ip_olt': '10.125.20.183'})
        ordenes = [list(row) for row in query]

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
finally:
 
    logging.debug('fallo')
