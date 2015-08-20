class graph_helper:
        """ Class used to perform various operations on networks and graphs
        """
        
        class _node:
                """ Helper class for disjoint-sets data structure
                """
                def __init__(self, data, parent=None, rank = 0):
                        if parent == None:
                                parent = self
                        self.data   = data
                        self.parent = parent
                        self.rank   = rank
                
                @staticmethod
                def find(n):
                        if n != n.parent:
                                n.parent = graph_helper._node.find(n.parent)
                        return n.parent
                
                @staticmethod
                def merge(n, m):
                        s1 = graph_helper._node.find(n)
                        s2 = graph_helper._node.find(m)
                        if s1.rank > s2.rank:
                                s2.parent = s1
                        else:
                                s1.parent = s2
                                s2.rank += 1
                        

        def __init__(self, nodes, adj_function):
                """ Initialize a graph with the given set of nodes and given
                    adjacency function. The adjacency function will be used
                    to determine which nodes have edges between them. It should
                    return a list of nodes adjacent to the node given as the
                    parameter. For example, if each node object has an attribute
                    called 'edges' which gives the necessary list: 
                            adj_function = lambda x: x.edges
                """
                self.nodes = nodes[:]
                self.adjf = adj_function
        
        def _dfs_cc_helper(self, djs, visited, node):
                """ Run DFS on a particular node, performing the appropriate
                    unions on the DJS data structure.
                """
                if not visited[node]:
                        visited[node] = True
                        for n in self.adjf(node):
                                graph_helper._node.merge(djs[n], djs[node])
                                self._dfs_cc_helper(djs, visited, n)
        
        def dfs_connected_components(self):
                """ Run DFS on the graph and return a list of lists, giving the
                    connected components.
                """
                djs = {}
                visited = {}
                collect = {}
                for n in self.nodes:
                        djs[n] = graph_helper._node(n)
                        visited[n] = False
                for n in self.nodes:
                        self._dfs_cc_helper(djs, visited, n)
                for n in self.nodes:
                        p = graph_helper._node.find(djs[n])
                        if not p in collect:
                                collect[p] = []
                        collect[p].append(n)
                return [collect[k] for k in collect]
