from core import pycore, misc, mobility, netns, api
import xml.etree.ElementTree
import re

class session_helper(pycore.Session):
        """
        Create a CORE session containing the nodes and interfaces defined
        in the given XML session definition.          
            
        Each wireless network in the topology will use the BasicRangeModel
        with the default parameters to determine adjacencies.
            
        CORE behaves badly when importing an XML session, making it
        necessary to copy each node and interface into a new session. The
        temporary session loaded from the XML file is shutdown after it
        has been copied into the new session.
        """

        def __init__(self, xml_file):
                """ Instantiate a session based on the given xml file.
                """
                super(session_helper, self).__init__()
                self._xml_file = xml_file
                self._import()
        
        def _model_params(self, net_name):
                """ Retrieves the parameters of the basic_range model used on
                    the network with the given net_name.
                """
        
                # open xml file
                tree = xml.etree.ElementTree.parse(self._xml_file)
                root = tree.getroot()
                
                # use default params if the network is not found
                parms = {
                        'range':     275,
                        'bandwidth': 54000000,
                        'jitter':    0,
                        'delay':     20000,
                        'error':     0
                }
                
                # locate this network and extract its parameters
                for e in root.findall("network"):
                        if e.get('name') == net_name:
                                continue
                        chan = e.find("channel")
                        cmod = chan.find("type")
                        cpar = chan.findall("parameter")
                        if cmod.text != "basic_range":
                                raise Exception("This network uses a model other than basic_range. Only the basic_range model is supported at this time.")
                        for p in cpar:
                                parms[p.get("name")] = p.text
                        break
                
                # return the parameters as a list
                return [parms['range'], parms['bandwidth'], parms['jitter'], parms['delay'], parms['error']]
                        
        
        def _import(self):
                """ Internal routine: create a temporary session and import
                    nodes and interfaces from it.
                """
        
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
                                wn.setmodel(mobility.BasicRangeModel, self._model_params(wo.name))
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
                """ Returns a list of CoreNode objects contained in the session
                """
                return [x for x in self.objs() if isinstance(x, netns.nodes.CoreNode)]
        
        def get_adjacencies(self, node):
                """ Returns a list of nodes adjacent to the node given as an argument
                """
                l = [x for x in node.netifs() if isinstance(x.net, netns.nodes.WlanNode)][0].net
                r = []
                with l._linked_lock:
                        for a in l._linked:
                                for b in l._linked[a]:
                                        if l._linked[a][b] and (a.node == node or b.node == node):
                                                r.append(list(set([a.node, b.node]) - set([node]))[0])
                return r
        
        @staticmethod
        def _aggregate_addrlist(node):
                """ Returns a list of all IP addresses associated with a node
                """
                l = []
                for i in node.netifs():
                        l.extend(i.addrlist)
                return l
                
        @staticmethod
        def addr_of(node):
                """ Returns the first IPv4 address of a particular node
                """
                return session_helper.get_ipv4_addr(session_helper._aggregate_addrlist(node))
        
        @staticmethod
        def get_ipv4_addr(addr_list):
                """
                Given a list of strings, return the first one that looks like an
                IPv4 address. Returns None if no IPv4 address is found.
                
                The addresses may be CIDR addresses, e.g. 10.0.0.0/24; in this
                case, only the actual address will be returned and the mask will
                be omitted.
                """
                exp = re.compile("^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})(\/[0-9]{1,2})?$")
                for ip in addr_list:
                        m = exp.search(ip)
                        if m != None:
                                return m.group(1)
                return None
