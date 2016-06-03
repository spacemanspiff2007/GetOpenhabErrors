# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 13:43:06 2016

@author: gesebas
"""

import requests
import base64


class oh_rest:
    
    def __init__(self, host, port, user = "", pw = ""):
        self.openhab_host   = host
        self.openhab_port   = port
        self.username       = user
        self.password       = pw


    def post_command(self, key, value):
        """ Post a command to OpenHAB - key is item, value is command """
        url = 'http://%s:%s/rest/items/%s'%(self.openhab_host,
                                    self.openhab_port, key)
        req = requests.post(url, data=value,
                                headers=self.basic_header())
        if req.status_code != requests.codes.ok:
            req.raise_for_status()
    
    def put_status(self, key, value):
        """ Put a status update to OpenHAB  key is item, value is state """
        url = 'http://{:s}:{:s}/rest/items/{:s}/state'.format(self.openhab_host,
                                    self.openhab_port, key)
        req = requests.put(url, data=value, headers=self.basic_header())
        if req.status_code != requests.codes.ok:
            req.raise_for_status()    
            
    
    def basic_header(self):
        
        """ Header for OpenHAB REST request - standard """
        self.auth = str(base64.b64encode( ('{:s}:{:s}'.format(self.username, self.password)).encode() ))
        self.auth.replace("\n", "")
        return {
                "Authorization" : "Basic {:s}".format( self.auth), 
                "Content-type": "text/plain"}