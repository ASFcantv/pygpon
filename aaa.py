import base64
import os
import requests
from pathlib import Path
from xml.etree import ElementTree
import xmltodict
import json
from datetime import datetime as dt
import socket

now=dt.now()
nombre_pc=socket.gethostname()
remoteAddress=socket.gethostbyname(nombre_pc)


class aaa:
    def crear(imsi,numero_identificador,subscriberid,product_id):   
        
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
            return "error"   
            
        pic=consulta_suscriptor.text

        if pic.find('Operation successfully')>-1:
            return "exitoso"
        elif pic.find('already exists')>-1:
             return "ya existe"
        else:
            return "error"
    
    def eliminar(subscriberid):        
        url='http://picpw10:8801/mule/services/AP901EliminarSuscriptorAba';
        xml="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:mul="http://MuleEliminarSuscriptorAba/" xmlns:mul1="http://MuleEliminarSuscriptorAba">
        <soapenv:Header/>
            <soapenv:Body>
                <mul:EliminarSuscriptor>
                  <!--Optional:-->
                  <mul:arg0>
                     <!--Optional:-->
                     <mul1:IDCLIENTEPIC>GPON</mul1:IDCLIENTEPIC>
                     <!--Optional:-->
                     <mul1:remoteAddress></mul1:remoteAddress>
                     <!--Optional:-->
                     <mul1:sequenceId></mul1:sequenceId>
                     <!--Optional:-->
                     <mul1:serialNo></mul1:serialNo>
                     <!--Optional:-->
                     <mul1:subscriberID>"""+subscriberid+"""</mul1:subscriberID>
                     <!--Optional:-->
                     <mul1:timeStampSN></mul1:timeStampSN>
                  </mul:arg0>
                </mul:EliminarSuscriptor>
            </soapenv:Body>
        </soapenv:Envelope>"""

        try:
            consulta_suscriptor=requests.post(url,data=xml,timeout=50) 
        except:
            return "error"   
            
        pic=consulta_suscriptor.text

        if pic.find('Operation successfully')>-1:
            return "exitoso"
        elif pic.find('does not exist')>-1:
             return "no existe"
        else:
            return "error"

    def consultarSuscriptor(subscriberid):
        url='http://picpw10:8801/mule/services/AP904ConsultarProductosAba'
        xml="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:mul="http://MULEConsultarProductosAba/" xmlns:mul1="http://MULEConsultarProductosAba">
            <soapenv:Header/>
            <soapenv:Body>
                <mul:ConsultarProductos>
                  <!--Optional:-->
                  <mul:arg0>
                     <!--Optional:-->
                     <mul1:IDCLIENTEPIC>GPON</mul1:IDCLIENTEPIC>
                     <!--Optional:-->
                     <mul1:remoteAddress></mul1:remoteAddress>
                     <!--Optional:-->
                     <mul1:sequenceId></mul1:sequenceId>
                     <!--Optional:-->
                     <mul1:serialNo></mul1:serialNo>
                     <!--Optional:-->
                     <mul1:subscriberID>"""+subscriberid+"""</mul1:subscriberID>
                     <!--Optional:-->
                     <mul1:timeStampSN></mul1:timeStampSN>
                  </mul:arg0>
                </mul:ConsultarProductos>
            </soapenv:Body>
        </soapenv:Envelope>"""

        try:
            consulta_suscriptor=requests.post(url,data=xml,timeout=50) 
        except:
            return "error"   
            
        pic=consulta_suscriptor.text

        if pic.find('Operation successfully')>-1:
            return "exitoso"
        elif pic.find('Fault occurred while processing')>-1:
             return "no existe"            
        else:
            return "error"
                
       

    def consultarProducto(subscriberid):   
        url='http://picpw10:8801/mule/services/AP904ConsultarProductosAba'
        xml="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:mul="http://MULEConsultarProductosAba/" xmlns:mul1="http://MULEConsultarProductosAba">
                    <soapenv:Header/>
                    <soapenv:Body>
                        <mul:ConsultarProductos>
                          <!--Optional:-->
                          <mul:arg0>
                             <!--Optional:-->
                             <mul1:IDCLIENTEPIC>GPON</mul1:IDCLIENTEPIC>
                             <!--Optional:-->
                             <mul1:remoteAddress></mul1:remoteAddress>
                             <!--Optional:-->
                             <mul1:sequenceId></mul1:sequenceId>
                             <!--Optional:-->
                             <mul1:serialNo></mul1:serialNo>
                             <!--Optional:-->
                             <mul1:subscriberID>"""+subscriberid+"""</mul1:subscriberID>
                             <!--Optional:-->
                             <mul1:timeStampSN></mul1:timeStampSN>
                          </mul:arg0>
                        </mul:ConsultarProductos>
                    </soapenv:Body>
                </soapenv:Envelope>"""

        try:
            consulta_suscriptor=requests.post(url,data=xml,timeout=50) 
        except:
            return "error"   
            
        pic=consulta_suscriptor.text

        if pic.find('Operation successfully')>-1:
            
            xml_str=xmltodict.parse(pic)
            json_object = json.dumps(xml_str) 
            print(json_object)
        elif pic.find('Fault occurred while processing')>-1:
             return "no existe"            
        else:
            return "error"
        
    def modificarProducto(productid,subscriberid):
        url='http://picpw10:8801/mule/services/AP905ModificarProductosAba'
        xml="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:mul="http://MULEModificarProductosAba/" xmlns:mul1="http://MULEModificarProductosAba">
                <soapenv:Header/>
                <soapenv:Body>
                <mul:ModificarProducto>
                    <!--Optional:-->
                    <mul:arg0>
                        <!--Optional:-->
                        <mul1:IDCLIENTEPIC>GPON</mul1:IDCLIENTEPIC>
                        <!--Optional:-->
                        <mul1:effectTime></mul1:effectTime>
                        <!--Optional:-->
                        <mul1:productID>"""+productid+"""</mul1:productID>
                        <!--Optional:-->
                        <mul1:remoteAddress></mul1:remoteAddress>
                        <!--Optional:-->
                        <mul1:sequenceId></mul1:sequenceId>
                        <!--Optional:-->
                        <mul1:serialNo></mul1:serialNo>
                        <!--Optional:-->
                        <mul1:status>1</mul1:status>
                        <!--Optional:-->
                        <mul1:subscriberID>"""+subscriberid+"""</mul1:subscriberID>
                        <!--Optional:-->
                        <mul1:timeStampSN></mul1:timeStampSN>
                    </mul:arg0>
                </mul:ModificarProducto>
                </soapenv:Body>
            </soapenv:Envelope>"""

        try:
            consulta_suscriptor=requests.post(url,data=xml,timeout=50) 
        except:
            return "error"   
            
        pic=consulta_suscriptor.text

        if pic.find('Operation successfully')>-1:
            return "exitoso"
        elif pic.find('has subscribed to location service')>-1:
             return "no existe"
        else:
            return "error"