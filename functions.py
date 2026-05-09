import os
import datetime
from collections import deque

# ──────────────────────────────────────────────
#  Item class
# ──────────────────────────────────────────────
class Item:
    def __init__(self, name: str = "", description: str = "", category: str = "", price: int = 0, quantity: int = 0, loc_x: int = 0, loc_y: int = 0):
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.quantity = quantity
        self.loc_x = loc_x
        self.loc_y = loc_y

# ──────────────────────────────────────────────
#  AVL Tree Node
# ──────────────────────────────────────────────
class TreeNode:
    def __init__(self, item: Item = None):
        self.data = item if item else Item()
        self.left = None
        self.right = None
        self.height = 0

# ──────────────────────────────────────────────
#  Transaction Logging
# ──────────────────────────────────────────────
def log_transaction(txn_type: str, item_name: str, quantity: int) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open("transactions.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {txn_type.upper():<8} | {item_name} | Qty: {quantity}\n")
    except IOError:
        pass

# ──────────────────────────────────────────────
#  AVL Tree helper functions
# ──────────────────────────────────────────────
def height(node: TreeNode) -> int:
    if node is None:
        return -1
    return node.height

def balance_factor(node: TreeNode) -> int:
    if node is None:
        return 0
    return height(node.left) - height(node.right)

def right_rotate(y: TreeNode) -> TreeNode:
    x = y.left
    t2 = x.right if x else None

    x.right = y
    y.left = t2
    
    y.height = 1 + max(height(y.left), height(y.right))
    x.height = 1 + max(height(x.left), height(x.right))
    return x

def left_rotate(x: TreeNode) -> TreeNode:
    y = x.right
    t2 = y.left if y else None

    y.left = x
    x.right = t2
    
    x.height = 1 + max(height(x.left), height(x.right))
    y.height = 1 + max(height(y.left), height(y.right))
    return y

# ──────────────────────────────────────────────
#  AVL Insert
# ──────────────────────────────────────────────
def avl_insert(root: TreeNode, item: Item) -> TreeNode:
    if root is None:
        return TreeNode(item)

    if item.name < root.data.name:
        root.left = avl_insert(root.left, item)
    else:
        root.right = avl_insert(root.right, item)

    root.height = 1 + max(height(root.left), height(root.right))
    balance = balance_factor(root)

    # Left-Left
    if balance > 1 and item.name < root.left.data.name:
        return right_rotate(root)

    # Right-Right
    if balance < -1 and item.name > root.right.data.name:
        return left_rotate(root)

    # Left-Right
    if balance > 1 and item.name > root.left.data.name:
        root.left = left_rotate(root.left)
        return right_rotate(root)

    # Right-Left
    if balance < -1 and item.name < root.right.data.name:
        root.right = right_rotate(root.right)
        return left_rotate(root)

    return root

# ──────────────────────────────────────────────
#  AVL Search
# ──────────────────────────────────────────────
def avl_search(root: TreeNode, name: str) -> TreeNode:
    if root is None or root.data.name == name:
        return root
    if name < root.data.name:
        return avl_search(root.left, name)
    return avl_search(root.right, name)

# ──────────────────────────────────────────────
#  AVL In-order display
# ──────────────────────────────────────────────
def in_order(root: TreeNode) -> None:
    if root is None:
        return
    in_order(root.left)
    i = root.data
    print(f"{i.name:<18}{i.description:<60}{i.category:<15}{i.price:>12}{i.quantity:>15}")
    in_order(root.right)

# ──────────────────────────────────────────────
#  AVL Delete
# ──────────────────────────────────────────────
def avl_delete(root: TreeNode, name: str) -> TreeNode:
    if root is None:
        return root

    if name < root.data.name:
        root.left = avl_delete(root.left, name)
    elif name > root.data.name:
        root.right = avl_delete(root.right, name)
    else:
        # Node with one or no children
        if root.left is None or root.right is None:
            return root.left if root.left else root.right

        # In-order successor (smallest in right subtree)
        temp = root.right
        while temp.left is not None:
            temp = temp.left
        root.data = temp.data
        root.right = avl_delete(root.right, temp.data.name)

    root.height = 1 + max(height(root.left), height(root.right))
    balance = balance_factor(root)

    if balance > 1 and balance_factor(root.left) >= 0:
        return right_rotate(root)

    if balance > 1 and balance_factor(root.left) < 0:
        root.left = left_rotate(root.left)
        return right_rotate(root)

    if balance < -1 and balance_factor(root.right) <= 0:
        return left_rotate(root)

    if balance < -1 and balance_factor(root.right) > 0:
        root.right = right_rotate(root.right)
        return left_rotate(root)

    return root

# ──────────────────────────────────────────────
#  File I/O
# ──────────────────────────────────────────────
CATALOGUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalogue.txt")

def load_catalogue_to_avl() -> TreeNode:
    root = None
    if not os.path.exists(CATALOGUE_FILE):
        return root

    try:
        import random
        with open(CATALOGUE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) < 5:
                    continue
                try:
                    # Default to Dispatch area (0,0) if no coords
                    lx = int(parts[5]) if len(parts) > 5 else 0
                    ly = int(parts[6]) if len(parts) > 6 else 0
                    item = Item(
                        name=parts[0],
                        description=parts[1],
                        category=parts[2],
                        price=int(parts[3]),
                        quantity=int(parts[4]),
                        loc_x=lx,
                        loc_y=ly
                    )
                    root = avl_insert(root, item)
                except ValueError:
                    # Skip corrupted numeric fields smoothly
                    continue
    except IOError:
        pass

    return root

def save_to_file(root: TreeNode) -> None:
    """Saves the AVL tree back to text format in alphabetical (in-order) sequence."""
    if root is None:
        try:
            open(CATALOGUE_FILE, "w").close()
        except IOError:
            pass
        return

    try:
        with open(CATALOGUE_FILE, "w", encoding="utf-8") as f:
            def _write_in_order(node):
                if node is None:
                    return
                _write_in_order(node.left)
                it = node.data
                f.write(f"{it.name}\t{it.description}\t{it.category}\t{it.price}\t{it.quantity}\t{it.loc_x}\t{it.loc_y}\n")
                _write_in_order(node.right)
                
            _write_in_order(root)
    except IOError:
        pass