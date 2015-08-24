from generic_test import generic_test
from jadhoc import Jadhoc

class jadhoc_test (generic_test):

        def config_services(self):
                """ Install jadhoc service on each node
                """
                for n in self.nodes:
                        self.session.services.addservicestonode(n, None, "Jadhoc|IPForward", False)
                        self.session.services.bootnodeservices(n)
