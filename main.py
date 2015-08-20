from utils import session_helper, graph_helper
import argparse, itertools, time

def test_main(filename):
        """ Imports a topology from the given XML file and tests communication
            between each pair of nodes.
        """

        # load xml file
        session = session_helper(filename)
        
        # get nodes
        nodes = session.get_nodes()

        # test communication between each pair of nodes
        #for x, y in itertools.product(nodes, nodes):
        #        if x != y:
        #                addr_x = session_helper.addr_of(x)
        #                addr_y = session_helper.addr_of(y)
        #                print("ping %s -> %s" % (addr_x, addr_y))
        #                x.icmd(["bash", "-c", "ping -c 1 %s | tail -2 | head -1" % addr_y])
        #                print("")
        #session.get_adjacencies(nodes[0])
        g = graph_helper(nodes, session.get_adjacencies)
        cc = g.dfs_connected_components()
        for c in cc:
                print("New component: ")
                for n in c:
                        print(n.name)
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
