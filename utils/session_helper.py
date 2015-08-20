from core import pycore, misc, mobility, netns, api
import re

class session_helper(pycore.Session):

        def __init__(self, xml_file):
                super(session_helper, self).__init__()
                self._xml_file = xml_file
                self._import()
        
        def _import(self):
        
                # create temp session from which to import nodes and interfaces
                tmp = pycore.Session()
                misc.xmlsession.opensessionxml(tmp, self._xml_file)
        
                # remember new and old wlan objects
                wn = None
                wo = None
        
                # import objects
                for o in tmp.objs():
                        if isinstance(o, netns.nodes.WlanNode):
                                wo = o
                                wn = self.addobj(netns.nodes.WlanNode, name=wo.name)
                                x, y, z = wo.getposition()
                                wn.setposition(x, y, z)
                                wn.setmodel(mobility.BasicRangeModel, [275, 54000000, 0, 20000, 0])
                        elif isinstance(o, netns.nodes.CoreNode):
                                n = self.addobj(netns.nodes.CoreNode, name=o.name)
                                x, y, z = o.getposition()
                                n.setposition(x, y, z)
                        else:
                                raise Exception("object of unknown class: %s" % o)

                # import interfaces
                for i in wo.netifs():
                        o = self.objbyname(i.node.name)
                        o.newnetif(net=wn, addrlist=i.addrlist)
                                
                # close import session
                tmp.shutdown()
        
        def get_nodes(self):
                return [x for x in self.objs() if isinstance(x, netns.nodes.CoreNode)]
        
        @staticmethod
        def _aggregate_addrlist(node):
                l = []
                for i in node.netifs():
                        l.extend(i.addrlist)
                return l
                
        @staticmethod
        def addr_of(node):
                return session_helper.get_ipv4_addr(session_helper._aggregate_addrlist(node))
        
        @staticmethod
        def get_ipv4_addr(addr_list):
                """
                Given a list of strings, return the first one that looks like an
                IPv4 address. Returns None if no IPv4 address is found.
                """
                exp = re.compile("^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})(\/[0-9]{1,2})?$")
                for ip in addr_list:
                        m = exp.search(ip)
                        if m != None:
                                return m.group(1)
                return None
