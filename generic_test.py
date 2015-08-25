from utils import session_helper, graph_helper
import itertools, tempfile, re

class generic_test :

        def one_ping(self, x, y):
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
                tmp.close()
                if res == None:
                        return [False, 0, 0]
                else:
                        return [True, int(res.group(1)), float(res.group(2))]
        
        def test_pair(self, x, y):
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
                total_recv = []
                
                for i in range(0, self.establishment_phase):
                        success, ttl, latency = self.one_ping(x, y)
                        if success: break
                else:
                        return (False, [])
                        
                for i in range(0, self.collection_phase):
                        success, ttl, latency = self.one_ping(x, y)
                        if success:
                                total_recv.append((ttl, latency))
                
                return ((len(total_recv) / self.collection_phase) > self.loss_thresh, total_recv)
        
        def config_services(self):
                """ Configures node services
                """
                raise NotImplementedError("You cannot instantiate a generic_test! Use a subclass instead.")
        
        def __init__(self, filename, establishment_phase = 5, collection_phase = 5, loss_thresh = 0.95):
                """ Imports a topology from the given XML file and configures node services
                """
                
                # save test parameters
                self.establishment_phase = establishment_phase
                self.collection_phase = collection_phase
                self.loss_thresh = loss_thresh
        
                # load xml file
                self.session = session_helper(filename)
                
                # get nodes
                self.nodes = self.session.get_nodes()
        
                # init services
                self.config_services()
                        
        def do_test(self):
                """ Run the tests
                """
                res = {}
        
                # test communication between each pair of nodes in each connected component
                g = graph_helper(self.nodes, self.session.get_adjacencies)
                cc = g.dfs_connected_components()
                for c in cc:
                        for x, y in itertools.product(c, c):
                                if x != y:
                                       res[(x.name, y.name)] = self.test_pair(x, y) 
                return res
        
        def close(self):
                # end scenario
                self.session.shutdown()
