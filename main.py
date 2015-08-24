from utils import session_helper, graph_helper
import argparse, itertools, time, tempfile, re
from core import service
from jadhoc import Jadhoc

def one_ping(x, y):
        """ Sends one ping from node x to node y and records the results.
            Returns a list [success, ttl, time] where success is True or False
            depending on whether a reply was received, TTL is the integer value
            of the TTL field in the reply, and time is the reply latency in
            milliseconds. If success is False, then TTL and time will always
            be 0.
        """
        addr_y = session_helper.addr_of(y)
        pat = re.compile("^[0-9]+ bytes from (?:[0-9]{1,3}\.){3}[0-9]{1,3}\: icmp_seq=(?:[0-9]+) ttl=([0-9]+) time=([0-9]+(?:\.[0-9]+)?) ms$")
        tmp = tempfile.NamedTemporaryFile()
        x.icmd(["bash", "-c", "ping -c 1 %s | head -2 | tail -1 > %s" % (addr_y, tmp.name)])
        res = pat.match(tmp.read())
        
        if res == None:
                return [False, 0, 0]
        else:
                return [True, int(res.group(1)), float(res.group(2))]

def test_pair(x, y):
        """ Performs the test sequence for flow x -> y. The test sequence
            occurs in two phases. The first phase is the establishment phase,
            wherein up to 5 pings will be sent from x -> y to ensure that a
            route is available. The establishment phase ends as soon as a ping
            reply is received. If no reply is received after 5 attempts, the
            test is considered a failure and the collection phase is not
            entered. If the connection phase is entered, 5 more pings will be
            sent. The TTLs and latencies of each of these pings will be 
            recorded. This method always returns a tuple (success, log) where
            success is True or False, telling us whether the loss rate in the
            collection phase was less than the 5% threshold. log is a list
            of (ttl, latency) tuples giving the TTL and latency results of
            each ping in the collection phase.
        """
        establishment_phase = 5
        collection_phase = 5
        total_recv = []
        loss_thresh = 0.95
        
        for i in range(0, establishment_phase):
                success, ttl, latency = one_ping(x, y)
                if success: break
        else:
                return (False, [])
                
        for i in range(0, collection_phase):
                success, ttl, latency = one_ping(x, y)
                if success:
                        total_recv.append((ttl, latency))
        
        return ((len(total_recv) / collection_phase) > loss_thresh, total_recv)

def test_main(filename):
        """ Imports a topology from the given XML file and tests communication
            between each pair of nodes.
        """

        # load xml file
        session = session_helper(filename)
        
        # get nodes
        nodes = session.get_nodes()
        
        # install jadhoc service on each node
        svcs = session.services
        for n in nodes:
                svcs.addservicestonode(n, None, "Jadhoc|IPForward", False)
                session.services.bootnodeservices(n)

        # test communication between each pair of nodes in each connected component
        g = graph_helper(nodes, session.get_adjacencies)
        cc = g.dfs_connected_components()
        for c in cc:
                for x, y in itertools.product(c, c):
                        if x != y:
                               print("%s -> %s: " % (x.name, y.name))
                               r = test_pair(x, y) 
                               print(r)

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
