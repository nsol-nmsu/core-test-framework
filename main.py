from utils import session_helper, graph_helper
import argparse, itertools, time
from core import service
from jadhoc import Jadhoc

def test_main(filename):
        """ Imports a topology from the given XML file and tests communication
            between each pair of nodes.
        """

        # load xml file
        session = session_helper(filename)
        
        # get nodes
        nodes = session.get_nodes()
        
        # install jadhoc service on each node
        svcs = session.services #service.CoreServices(session)
        for n in nodes:
                svcs.addservicestonode(n, None, "Jadhoc|IPForward", False)
                session.services.bootnodeservices(n)
        
        for n in nodes:
                print("%s" % n.name)
                n.icmd(["ps", "aux"])
                print("")

        # test communication between each pair of nodes in each connected component
        g = graph_helper(nodes, session.get_adjacencies)
        cc = g.dfs_connected_components()
        for c in cc:
                for x, y in itertools.product(c, c):
                        if x != y:
                                addr_x = session_helper.addr_of(x)
                                addr_y = session_helper.addr_of(y)
                                print("ping %s -> %s" % (addr_x, addr_y))
                                x.icmd(["bash", "-c", "ping -c 10 %s | tail -2 | head -1" % addr_y])
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
