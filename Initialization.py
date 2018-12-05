import random
import numpy as np
class IniGraph():
    def __init__(self, dataname):
        ### dataname, data_data_path, data_weight_path, data_degree_path: (str)
        self.dataname = dataname
        self.data_data_path = "data/" + dataname + "/" + dataname + "_data.txt"
        self.data_weight_path = "data/" + dataname + "/" + dataname + "_weight.txt"
        self.data_degree_path = "data/" + dataname + "/" + dataname + "_degree.txt"

    def setEdgeWeight(self):
        #  -- set weight on edge --
        fw = open(self.data_weight_path, 'w')
        with open(self.data_data_path) as f:
            for line in f:
                (key, val) = line.split()
                # --- output: first node, second node, weight on the edge within nodes ---
                fw.write(key + " " + val + " " + str(round(random.random(), 2)) + "\n")
        fw.close()
        f.close()

    def countNodeOutdegree(self):
        #  -- count the out-degree --
        ### numnode: (int) the number of nodes in data
        fw = open(self.data_degree_path, 'w')
        with open(self.data_data_path) as f:
            numnode = 0
            list = []
            for line in f:
                (node1, node2) = line.split()
                numnode = max(numnode, int(node1), int(node2))
                list.append(node1)

        for i in range(0, numnode + 1):
            # --- output: node, the cost of the node ---
            fw.write(str(i) + " " + str(list.count(str(i))) + "\n")
        fw.close()
        f.close()

    def constructSeedCostDict(self):
        # -- calculate the cost for each seed
        ### seedcost: (dict) the set of cost for each seed
        ### seedcost[i]: (float2) the degree of i's seed
        ### numnode: (int) the number of nodes in data
        ### maxdegree: (int) the maximum degree in data
        seedcost = {}
        with open(self.data_degree_path) as f:
            numnode, maxdegree = 0, 0
            list = []
            for line in f:
                (node, degree) = line.split()
                numnode = max(numnode, int(node))
                maxdegree = max(maxdegree, int(degree))
                list.append([node, degree])
            for i in range(numnode + 1):
                seedcost[str(i)] = round(int(list[i][1]) / maxdegree, 2)
        f.close()
        return seedcost

    def constructGraphDict(self):
        # -- build graph --
        ### graph: (dict) the graph
        ### graph[node1]: (dict) the set of node1's receivers
        ### graph[node1][node2]: (str) the weight one the edge of node1 to node2
        graph = {}
        with open(self.data_weight_path) as f:
            for line in f:
                (node1, node2, wei) = line.split()
                if node1 in graph:
                    graph[node1][node2] = str(wei)
                else:
                    graph[node1] = {node2: str(wei)}
        f.close()
        return graph

    def setNodeWallet(self, product_name, upper):
        # -- set node's personal budget (wallet) --
        fw = open("data/" + self.dataname + "/" + self. dataname + "_wallet_r" + list(product_name)[6] + "p" + list(product_name)[8] + "n" + list(product_name)[10] + ".txt", 'w')
        with open(self.data_degree_path) as f:
            for line in f:
                (key, val) = line.split()
                # --- first node, second node, weight on the edge within nodes ---
                fw.write(key + " " + str(round(random.uniform(0, upper), 2)) + "\n")
        fw.close()
        f.close()

    def getWalletList(self, product_name):
        wallet_list = []
        with open("data/" + self.dataname + "/" + self. dataname + "_wallet_r" + list(product_name)[6] + "p" + list(product_name)[8] + "n" + list(product_name)[10] + ".txt") as f:
            for line in f:
                (nnode, wallet) = line.split()
                wallet_list.append(float(wallet))
        f.close()
        return wallet_list

class IniProduct():
    def setRatioDiffPriceDiff(self, numratio, numprice):
        # -- set the price with different ratios and prices
        ### rlist: (list) the list to record different ratio
        ### rlist[num]: (float2) the bias ratio for output ratio
        ### plist: (list) the list to record different price
        ### plist[num]: (float2) the bias price for output price
        rlist, plist = [], []

        # -- set the bias ratio --
        # -- the multiple between each bias ratio has to be greater than 2 --
        ### dr: (int) the definition of ratio
        dr = 1
        while dr:
            for r in range(numratio):
                rlist.append(round(random.uniform(0, 2), 2))
                rlist.sort()

            if 0.0 in rlist:
                continue

            for r in range(len(rlist) - 1):
                if rlist[r + 1] / rlist[r] < 2 or rlist[r + 1] - rlist[r] < 0.1 or rlist[r] < 0.1:
                    dr += 1
                    continue

            if dr == 1:
                dr = 0
            else:
                dr = 1
                rlist = []

        # -- set the bias price --
        # -- the difference between each bias price has to be greater than 0.1 --
        ### dp: (int) the definition of price
        dp = 1
        while dp:
            # -- make the base price fall in different intervals --
            for p in range(numprice):
                plist.append(round(random.uniform(p / numprice, (p + 1) / numprice), 2))

            for p in range(len(plist) - 1):
                if plist[p + 1] - plist[p] < 0.1 or plist[p] < 0.1:
                    dp += 1
                    continue

            if dp == 1:
                dp = 0
            else:
                dp = 1
                plist = []

        # -- set output products --
        ### productlist: (list) the set to record output products
        ### productlist[num]: (list) [num's profit, num's cost, num's ratio, num's price]
        ### productlist[num][]: (float2)
        productlist = []
        for r in range(len(rlist)):
            for p in range(len(plist)):
                price, profit, cost = 0.0, 0.0, 0.0
                while price == 0.0 or profit == 0.0 or cost == 0.0 or price > 1:
                    price = plist[p] + random.uniform(-0.5, 0.5) * 0.1
                    profit = round(price * (rlist[r] / (1 + rlist[r])), 2)
                    cost = round(price * (1 / (1 + rlist[r])), 2)
                    price = round(profit + cost, 2)
                productlist.append([profit, cost, round((profit / cost), 2), price])

        fw = open("product/prod_r" + str(numratio) + "p" + str(numprice) + "n1000.txt", 'w')
        fw.write(str(numratio) + " " + str(numprice) + "\n")
        for p, c, r, pr in productlist:
            fw.write(str(p) + " " + str(c) + " " + str(r) + " " + str(pr) + "\n")
        fw.close()

    def getProductlist(self, productname):
        ### product_list: (list) [profit, cost, price]
        ### sumprice: (float2) the sum of prices
        product_list = []
        sumprice = 0.0
        with open("product/" + productname + ".txt") as f:
            for l, line in enumerate(f):
                if l == 0:
                    (numratio, numprice) = line.split()
                    continue
                (p, c, r, pr) = line.split()
                sumprice += float(pr)
                product_list.append([float(p), float(c), round(float(p) + float(c), 2)])
        return product_list, round(sumprice, 2)

if __name__ == "__main__":
    ### productname: (str)
    ### data_name: (str) the graph dataset
    ### product_name: (str) the product dataset
    ### num_price: (int) the kinds of generated price
    ### num_ratio: (int) the kinds of generated ratio
    data_name = "email"
    product_name = "prod_r1p3n1"
    # num_ratio, num_price = 1, 3

    iniG = IniGraph(data_name)
    iniP = IniProduct()

    # iniG.setEdgeWeight()
    # iniG.countNodeOutdegree()

    # graph_dict = iniG.constructGraphDict()
    # seedcost_dict = iniG.constructSeedCostDict()
    # iniP.setRatioDiffPriceDiff(num_price, num_ratio)
    product_list, sum_price = iniP.getProductlist(product_name)
    # iniG.setNodeWallet(product_name, sum_price)
    wallet_list = iniG.getWalletList(product_name)

    print(wallet_list)
    print(np.array(wallet_list).shape)

