

# - - - - - - - - - - - - - - - - - - - - - - - - - -
class Tree:
# - - - - - - - - - - - - - - - - - - - - - - - - - -


    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, edges: dict):
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.edges = edges

    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_nodes_in_path_to_root(self, node):
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
        node_set = { node }
        while True:
            parent = self.edges.get(node)
            if parent is None: break
            node_set.add(parent)
            node = parent
        return node_set
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_closest_parent(self, node1, node2):
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
        set1 = self.get_nodes_in_path_to_root(node1)
        while True:
            if node2 in set1: return node2
            parent = self.edges.get(node2)
            if parent is None: return None
            node2 = parent
            
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_close_parent_set(self, node_set):
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(node_set) == 1: return set(node_set)
        old_set = set(node_set)   # copy of input set
        while True:
            print("iter")
            new_set = set()
            old_list = list(old_set)
            to_be_removed = set()
            for i in range(0, len(old_list)):
                for j in range(i+1, len(old_list)):
                    node1 = old_list[i]
                    node2 = old_list[j]
                    parent = self.get_closest_parent(node1, node2)
                    if parent is None:
                        new_set.add(node1)
                        new_set.add(node2)
                    else:
                        if node1 != parent: to_be_removed.add(node1)
                        if node2 != parent: to_be_removed.add(node2)
                        new_set.add(parent)
                    print(node1, node2, "=>", parent, ", new set:", new_set, ", will remove:", to_be_removed)
            if len(new_set)==1: break
            new_set = new_set - to_be_removed
            if len(new_set)==1: break
            if new_set == old_set: break  
            old_set = new_set
        return new_set



# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

    def test_closest_parent(tree, a,b, expected):
        parent = tree.get_closest_parent(a,b)
        result = "...OK" if parent == expected else "ERROR"
        print(result, "input:", a, b, "expected", expected, ", got", parent)

    def test_close_parent_set(tree, node_set, expected):
        parent_set = tree.get_close_parent_set(node_set)
        result = "...OK" if parent_set == expected else "ERROR"
        print(result, "input:", node_set, "expected", expected, ", got", parent_set)

    def test_close_parent_dic(tree, node_set, expected):
        parent_set = tree.get_close_parent_dic(node_set)
        result = "...OK" if parent_set == expected else "ERROR"
        print(result, "input:", node_set, "expected", expected, ", got", parent_set)



    edges = { "a1" : "a", "a2": "a", "a": "alpha", "d1": "alpha", "134": "num"}
    tree = Tree(edges)
    
    test_closest_parent(tree, "a", "b", None)
    test_closest_parent(tree, "a1", "a", "a")
    test_closest_parent(tree, "a", "a1", "a")
    test_closest_parent(tree, "a", "d1", "alpha")
    test_closest_parent(tree, "a1", "d1", "alpha")
    test_closest_parent(tree, "d1", "a1", "alpha")
    test_closest_parent(tree, "d1", "a", "alpha")
    test_closest_parent(tree, "num", "a1", None)
    test_closest_parent(tree, "a", "a", "a")
    print("---")
    test_close_parent_set(tree, {"a", "d1", "num"}, {"alpha", "num"})
    test_close_parent_set(tree, {"a1", "d1", "num"}, {"alpha", "num"})
    test_close_parent_set(tree, {"a", "num"}, {"a", "num"})
    test_close_parent_set(tree, {"a1", "a2"}, {"a"})
    test_close_parent_set(tree, {"a1"}, {"a1"})
    test_close_parent_set(tree, set(), set()) # careful: {} != set() !!!
    

