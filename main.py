from core import pycore, misc, mobility, netns, api
import argparse, itertools, time, re

def get_ipv4_addr(addr_list):
        """
        Given a list of strings, return the first one that looks like an
        IPv4 address. Returns None if no IPv4 address is found.
        """
        exp = re.compile("^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\/[0-9]{1,2}$")
        for ip in addr_list:
                m = exp.search(ip)
                if m != None:
                        return m.group(1)
        return None

def test_main(filename):
        """ Imports a topology from the given XML file and tests communication
            between each pair of nodes.
            
            Each wireless network in the topology will use the BasicRangeModel
            with the default parameters to determine adjacencies.
            
            CORE behaves badly when importing an XML session, making it
            necessary to copy each node and interface into a new session. The
            temporary session loaded from the XML file is shutdown after it
            has been copied into the new session.
        """

        # create temp session from which to import nodes and interfaces
        tmp = pycore.Session()
        misc.xmlsession.opensessionxml(tmp, filename)

        # create new session to import into
        session = pycore.Session()
        
        # remember new and old wlan objects
        wn = None
        wo = None
        
        # remember nodes
        nodes = []
        addrs = {}
        
        # import objects
        for o in tmp.objs():
                if isinstance(o, netns.nodes.WlanNode):
                        wo = o
                        wn = session.addobj(netns.nodes.WlanNode, name=wo.name)
                        x, y, z = wo.getposition()
                        wn.setposition(x, y, z)
                        wn.setmodel(mobility.BasicRangeModel, [275, 54000000, 0, 20000, 0])
                elif isinstance(o, netns.nodes.CoreNode):
                        n = session.addobj(netns.nodes.CoreNode, name=o.name)
                        x, y, z = o.getposition()
                        n.setposition(x, y, z)
                        nodes.append(n)
                else:
                        raise Exception("object of unknown class: %s" % o)

        # import interfaces
        for i in wo.netifs():
                o = session.objbyname(i.node.name)
                o.newnetif(net=wn, addrlist=i.addrlist)
                if not o in addrs:
                        addrs[o] = []
                addrs[o].extend(i.addrlist)
                
        # close import session
        tmp.shutdown()

        # test communication between each pair of nodes
        for x, y in itertools.product(nodes, nodes):
                if x != y:
                        addr_x = get_ipv4_addr(addrs[x])
                        addr_y = get_ipv4_addr(addrs[y])        
                        print("ping %s -> %s" % (addr_x, addr_y))
                        x.icmd(["bash", "-c", "ping -c 1 %s | tail -2 | head -1" % addr_y])
                        print("")

        # end scenario
        session.shutdown()

def main():
        """ Parses command line arguments and calls test_main.
        """

        parser = argparse.ArgumentParser()
        parser.add_argument('xml_file', type=str)
        args = parser.parse_args()
        test_main(args.xml_file)

if __name__ == "__main__" or __name__ == "__builtin__":
        main()
