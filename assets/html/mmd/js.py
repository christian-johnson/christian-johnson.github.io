import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
from tqdm import trange


def create_random_labeled_binary_tree(N, p):
    """
    Create a complete binary tree with N layers (depth N-1)
    and assign to each node a random label: 0 with probability p, 1 with probability 1-p.

    Parameters:
    - N (int): Number of layers (levels) in the binary tree.
    - p (float): Probability of labeling a node with 0.

    Returns:
    - G (networkx.DiGraph): A directed graph representing the binary tree.
    """
    G = nx.DiGraph()
    node_count = 0
    G.add_node(node_count, label=int(random.random() < p))
    current_layer = [node_count]
    node_count += 1

    for _ in range(1, N):
        next_layer = []
        for parent in current_layer:
            for _ in range(2):  # left and right child
                G.add_node(node_count, label=int(random.random() < p))
                G.add_edge(parent, node_count)
                next_layer.append(node_count)
                node_count += 1
        current_layer = next_layer

    return G


def get_path_label_sums(G):
    """
    For a binary tree G with node attribute 'label', compute the sum of labels for each root-to-leaf path.

    Parameters:
    - G: networkx.DiGraph (or Graph), assumed to be a binary tree with labeled nodes.

    Returns:
    - path_sums: list of ints, each is the sum of labels along a unique root-to-leaf path.
    """
    root = [n for n in G.nodes if G.in_degree(n) == 0][0]
    leaves = [n for n in G.nodes if G.out_degree(n) == 0]

    path_sums = []
    for leaf in leaves:
        path = nx.shortest_path(G, source=root, target=leaf)
        label_sum = sum(G.nodes[n]["label"] for n in path)
        path_sums.append(label_sum)

    return np.array(path_sums)


2**25


def count_paths(G):
    """
    Count the number of root-to-leaf paths in binary tree G where the sum of node labels is ≤ 1.

    Parameters:
    - G: networkx.DiGraph, binary tree with node attribute 'label' (0 or 1)

    Returns:
    - count: int, number of root-to-leaf paths with sum ≤ 1
    """
    root = [n for n in G.nodes if G.in_degree(n) == 0][0]

    def dfs(node, current_sum):
        if current_sum > 1:
            return 0  # early exit
        if G.out_degree(node) == 0:
            return 1  # reached a leaf with acceptable sum

        total = 0
        for child in G.successors(node):
            total += dfs(child, current_sum + G.nodes[child]["label"])
        return total

    return dfs(root, G.nodes[root]["label"])


def f0(p):
    """Odds of the tree having a zero-sum path given labeling probability p."""
    return 1 - (1 - np.sqrt(1 - 4 * p * (1 - p))) / (2 * p)


def p(f):
    """Given odds f of having a zero-sum path, what is the labeling probability?"""
    return


f0(0.75)

results = np.zeros((12))
for tree_size in np.arange(12):
    print(tree_size)
    count = 0
    N_iter = 5000
    for i in trange(N_iter):
        G = create_random_labeled_binary_tree(tree_size + 1, 1.0 - 0.5306035754)
        sums = get_path_label_sums(G)
        if np.any(sums <= 1):
            count += 1
    results[tree_size] = count / N_iter

plt.errorbar(
    np.arange(12) + 1, results, xerr=0, yerr=np.sqrt(results * N_iter) / N_iter
)
plt.axhline(0.5, ls="--")
plt.ylim([0, 1.0])
plt.xlim([0, 40.0])
plt.show()

p = 0.999
int(random.random() < p)

count = 0
N_iter = 500
for i in trange(N_iter):
    G = create_random_labeled_binary_tree(20, 1.0 - 0.53060)
    sums = count_paths(G)
    if sums > 0:
        count += 1
print(count / N_iter)

count - np.sqrt(count)


G = create_random_labeled_binary_tree(5, 1.0 - 0.6666)
count_paths(G)
