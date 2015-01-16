#coding:utf-8
import datetime
import urllib
import base64
import hmac
import hashlib
from elementtree.ElementTree import parse, fromstring

class Instance:
    def __init__(self, rolename, servername):
        self.rolename = rolename
        self.servername = servername

class Farm:
    def __init__(self, xml):
        self.xml = xml
        self.xmltree = None
        self.fname = None
        self.role_instances = []
        
    def tree(self):
        if self.xmltree == None:
            self.xmltree = fromstring(self.xml)
        return self.xmltree
        
    def name(self):
        if self.fname == None:
            self.fname = self.tree().find('Name').text
        return self.fname
    
#    def _get_instance_ids(self):
        #self.instance_ids = [cid.text for cid in self.tree().findall('FarmRoleSet/Item/ServerSet/Item/PlatformProperties/InstanceID')]
#        return self.instance_ids
    
    def get_unique_instances(self):
        if not self.role_instances:
            roles = self.tree().findall('FarmRoleSet/Item')
            for role in roles:
                nodename = role.find('ServerSet/Item/PlatformProperties/InstanceID')
                if nodename == None:
                    continue
                nodename = role.find('ServerSet/Item/PlatformProperties/InstanceID').text
                rolename = role.find('Name').text
                instance = Instance(rolename, nodename)
                self.role_instances.append(instance)
        return self.role_instances

class ScalrApiContext:
    def __init__(self, url, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.url = url
        self.version = '2.3.0'
        self.auth_version = '3'
        self.farms = {}
        self.farm_ids = []
    
    def scalr_api_fetch_xml(self, action, extraParams={}):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        genericParams = {
            "Action": action,
            "Version": self.version,
            "AuthVersion": self.auth_version,
            "Timestamp": timestamp,
            "KeyID": self.api_key,
            "Signature":  base64.b64encode(hmac.new(self.secret_key, ":".join([action, self.api_key, timestamp]), hashlib.sha256).digest()),
        }
        
        params = dict(genericParams.items() + extraParams.items())
    
        urlparams = urllib.urlencode(params)
        print "Querying {0} from {1} with params {2}".format(action, self.url, str(extraParams))
        req = urllib.urlopen(self.url, urlparams)
        print "Returned"
        return req.read()

    def scalr_api_fetch(self, action, extraParams={}):
        sxml = self.scalr_api_fetch_xml(action, extraParams)
        tree = fromstring(sxml)
        if (tree.tag == "Error"):
            message = tree.find('Message').text
            raise RuntimeError(message)
        return tree
    
    def get_farm(self, farm_id):
        if not self.farms.has_key(farm_id) == None:
            self.farms[farm_id] = Farm(self.scalr_api_fetch_xml('FarmGetDetails', {'FarmID':str(farm_id)}))
        return self.farms[farm_id]
    
    def get_farm_ids(self):
        if not self.farm_ids:
            tree = self.scalr_api_fetch('FarmsList')
            self.farm_ids = [fid.text for fid in tree.findall('FarmSet/Item/ID')]
        return self.farm_ids
        
    
    def get_farms(self):
        if not self.farms:
            for fid in self.get_farm_ids():
                farm = self.get_farm(fid)
                self.farms[fid] = farm
        farms = self.farms.values()
        return farms

def show_xml(s):
        import xml.dom.minidom
        xml = xml.dom.minidom.parseString(s)
        print xml.toprettyxml()