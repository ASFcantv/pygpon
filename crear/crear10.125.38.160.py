#!/usr/bin/env python3
import time
import logging
from datetime import datetime as dt
import socket
from db import engine
from sqlalchemy import text
from aprovisionar import *

#ips del olt traidas desde la ejecucion del archivo disparador.sh
ip_olt = '10.125.38.160'
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

        #confirmar si no trae ordenes
        if len(ordenes)>=2 :
            #aprovisionar
            aprovisionar.crear(ip_olt,ordenes)
finally:
 
    logging.debug('fallo')
