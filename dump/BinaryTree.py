class Node:
    def __init__(self, val):
        self.data = val
        self.left = None
        self.right = None

# Returns height which is the number of edges
# along the longest path from the root node down 
# to the farthest leaf node.
def height(root):
    if root is None:
        return 

    # compute the height of left and right subtrees
    lHeight = height(root.left)
    rHeight = height(root.right)

    return max(lHeight, rHeight) + 1

if __name__ == "__main__":
  
    # Representation of the input tree:
    #     12
    #    /  \
    #   8   18
    #  / \
    # 5   11
    root = Node(12)
    root.left = Node(8)
    root.right = Node(18)
    root.left.left = Node(5)
    root.left.right = Node(11)
    root.left.left.left = Node(9)


    print(height(root))