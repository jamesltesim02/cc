#!/usr/bin/python
# -*- coding: UTF-8 -*-


from models import purse,conn,cms,api
from .task import Task
import json


class CmsSyncGaming(Task):

    providerName = 'cms-provider'  
    conn = None
    def callback(self):
        print self.api.getCurrentGameList()
        
