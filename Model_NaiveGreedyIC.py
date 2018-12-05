import time
from Initialization import *

def sortSecond(val):
    return val[1]
def sortThird(val):
    return val[2]

class ModelNGIC():
    def __init__(self, graph_dict, seedcost_dict, product_list, total_budget, pp_strategy,
                 whether_infect_not_only_buying):
        ### graph_dict: (dict) the graph
        ### graph_dict[node1]: (dict) the set of node1's receivers
        ### graph_dict[node1][node2]: (float2) the weight one the edge of node1 to node2
        ### seedcost_dict: (dict) the set of cost for seeds
        ### seedcost_dict[i]: (dict) the degree of i's seed
        ### product_list: (list) the set to record products
        ### product_list[k]: (list) [k's profit, k's cost, k's price]
        ### product_list[k][]: (float2)
        ### total_ budget: (int) the budget to select seed
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### diffusion_threshold: (float2) the threshold to judge whether diffusion continues
        ### pp_strategy: (int) the strategy to upadate personal prob.
        ### whether_infect_not_only_buying: (bool) if infect when only after buying, then False
        self.graph_dict = graph_dict
        self.seedcost_dict = seedcost_dict
        self.product_list = product_list
        self.total_budget = total_budget
        self.num_node = len(seedcost_dict)
        self.num_product = len(product_list)
        self.diffusion_threshold = 0.01
        self.pp_strategy = pp_strategy
        self.whether_infect_not_only_buying = whether_infect_not_only_buying

    def getSeedExpectProfit(self, k_prod, i_node, a_n_set_k, cur_w_list, pp_list_k):
        # -- calculate the expected profit for single node when it's chosen as a seed --
        ### temp_a_n_set: (set) the union set of activated node set and temporary activated nodes when nnode is a new seed
        ### try_a_n_list: (list) the set to store the nodes may be activated for k-products
        ### try_a_n_list[][0]: (str) the receiver when i is ancestor
        ### try_a_n_list[][1]: (float4) the probability to activate the receiver from i
        ### try_a_n_list[][2]: (float2) the personal probability to activate ownself
        ### ep: (float2) the expected profit
        temp_a_n_set = a_n_set_k.copy()
        temp_a_n_set.add(i_node)
        try_a_n_list = []
        ep = -1 * self.seedcost_dict[i_node]

        # -- add the receivers of nnode into try_a_n_list --
        # -- notice: prevent the node from owing no receiver --
        if i_node not in self.graph_dict:
            return 0

        outdict = self.graph_dict[i_node]
        for out in outdict:
            if float(outdict[out]) >= self.diffusion_threshold and \
                    ((out not in temp_a_n_set and
                      cur_w_list[int(out)] > self.product_list[k_prod][2] and
                      pp_list_k[int(out)] > 0) or
                     self.whether_infect_not_only_buying):
                try_a_n_list.append([out,  float(outdict[out]), pp_list_k[int(out)]])

        while len(try_a_n_list) > 0:
            # -- add the value calculated by activated probability * profit of this product --
            if try_a_n_list[0][0] not in temp_a_n_set and \
                    cur_w_list[int(try_a_n_list[0][0])] > self.product_list[k_prod][2] and \
                    try_a_n_list[0][2] > 0:
                ep += try_a_n_list[0][1] * try_a_n_list[0][2] * self.product_list[k_prod][0]
            # -- add the receiver of node into try_a_n_list --
            # -- notice: prevent the node from owing no receiver --
            if try_a_n_list[0][0] not in self.graph_dict:
                del try_a_n_list[0]
                continue
            # -- activate the receivers temporally --
            temp_a_n_set.add(try_a_n_list[0][0])
            outdictw = self.graph_dict[try_a_n_list[0][0]]
            for outw in outdictw:
                if try_a_n_list[0][1] * float(outdictw[outw]) >= self.diffusion_threshold and \
                        ((outw not in temp_a_n_set and
                          cur_w_list[int(outw)] > self.product_list[k_prod][2] and
                          pp_list_k[int(outw)] > 0) or
                         self.whether_infect_not_only_buying):
                    try_a_n_list.append([outw, round(try_a_n_list[0][1] * float(outdictw[outw]), 4), pp_list_k[int(outw)]])
            del try_a_n_list[0]
        return round(ep, 4)

    def calAllSeedProfit(self, cur_w_list):
        # -- calculate expected profit for all combinations of nodes and products --
        ### expect_profit_list: (list) the list of expected profit for all combinations of nodes and products
        ### expect_profit_list[k]: (list) the list of expected profit for k-product
        ### expect_profit_list[k][i]: (float4) the expected profit for i-node for k-product
        expect_profit_list = []
        for k in range(self.num_product):
            expect_profit_list.append([])

        mngic = ModelNGIC(self.graph_dict, self.seedcost_dict, self.product_list, self.total_budget, self.pp_strategy,
                          self.whether_infect_not_only_buying)

        for k in range(self.num_product):
            for i in self.seedcost_dict:
                print(k, i)
                if i not in self.graph_dict:
                    ep = self.product_list[k][0] - self.seedcost_dict[i]
                else:
                    ep = mngic.getSeedExpectProfit(k, i, set(), cur_w_list, [1.0] * self.num_node)
                expect_profit_list[k].append(ep)
        return expect_profit_list

    def getMostValuableSeed(self, ep_list, nb_set, cur_budget):
        # -- find the seed with maximum expected profit from all combinations of nodes and products --
        ### mep: (list) the current maximum expected profit: [expected profit, which product, which node]
        mep = [0.0, 0, '-1']

        ### ban_set: (list) the set to record the node that will be banned
        ban_set = [set() for _ in range(self.num_product)]
        for k in range(self.num_product):
            for i in nb_set[k]:
                # -- the cost of seed cannot exceed the budget --
                if self.seedcost_dict[i] + cur_budget > self.total_budget:
                    # print(k, i, self.seedcost_dict[i] + cur_budget)
                    ban_set[k].add(i)
                    continue

                # -- the expected profit cannot be negative --
                if ep_list[k][int(i)] <= 0:
                    # print(k, i, ep_list[k][int(i)])
                    ban_set[k].add(i)
                    continue

                # -- choose the better seed --
                if ep_list[k][int(i)] > mep[0]:
                    mep = [ep_list[k][int(i)], k, i]

        for k in range(self.num_product):
            for i in ban_set[k]:
                if i in nb_set[k]:
                    nb_set[k].remove(i)

        return mep, nb_set

    def addSeedIntoSeedSet(self, k_prod, i_node, s_set, a_n_set, nb_set, cur_w_list, pp_list):
        # -- add the seed with maximum expected profit into seed set --
        s_set[k_prod].add(i_node)
        a_n_set[k_prod].add(i_node)
        for k in range(self.num_product):
            if i_node in nb_set[k]:
                nb_set[k].remove(i_node)
            pp_list[k][int(i_node)] = 0
        # print("into seedset: " + str(mep[2]))
        cur_profit = self.product_list[k_prod][0]
        cur_budget = self.seedcost_dict[i_node]
        cur_w_list[int(i_node)] = 0

        ### try_a_n_list: (list) the set to store the nodes may be activated for some products
        ### try_a_n_list[][0]: (str) the receiver when seed is ancestor
        ### try_a_n_list[][1]: (float4) the probability to activate the receiver from seed
        try_a_n_list = []
        # -- add the receivers of seed into try_a_n_list --
        # -- notice: prevent the seed from owing no receiver --
        if i_node not in self.graph_dict:
            return s_set, a_n_set, nb_set, cur_profit, cur_budget, cur_w_list, pp_list
        outdict = self.graph_dict[i_node]
        for out in outdict:
            if float(outdict[out]) >= self.diffusion_threshold and \
                    ((out not in a_n_set[k_prod] and
                      cur_w_list[int(out)] > self.product_list[k_prod][2] and
                      pp_list[k_prod][int(out)] > 0) or
                     self.whether_infect_not_only_buying):
                try_a_n_list.append([out, float(outdict[out]), pp_list[k_prod][int(out)]])

        # -- activate the candidate nodes actually --
        mngic = ModelNGIC(self.graph_dict, self.seedcost_dict, self.product_list, self.total_budget, self.pp_strategy,
                          self.whether_infect_not_only_buying)

        while len(try_a_n_list) > 0:
            if random.random() <= try_a_n_list[0][1] * try_a_n_list[0][2]:
                if try_a_n_list[0][0] not in a_n_set[k_prod] and \
                        cur_w_list[int(try_a_n_list[0][0])] > self.product_list[k_prod][2] and \
                        try_a_n_list[0][2] > 0:
                    a_n_set[k_prod].add(try_a_n_list[0][0])
                    cur_profit += self.product_list[k_prod][0]
                    cur_w_list[int(try_a_n_list[0][0])] -= self.product_list[k_prod][2]
                    pp_list = mngic.updatePersonalProbList(k_prod, try_a_n_list[0][0], cur_w_list, pp_list)

                if try_a_n_list[0][0] not in self.graph_dict:
                    del try_a_n_list[0]
                    continue

                outdictw = self.graph_dict[try_a_n_list[0][0]]
                for outw in outdictw:
                    if try_a_n_list[0][1] * float(outdictw[outw]) >= self.diffusion_threshold and \
                            ((outw not in a_n_set[k_prod] and
                              cur_w_list[int(outw)] > self.product_list[k_prod][2] and
                              pp_list[k_prod][int(outw)] > 0) or
                             self.whether_infect_not_only_buying):
                        try_a_n_list.append([outw, try_a_n_list[0][1] * float(outdictw[outw]), pp_list[k_prod][int(outw)]])
            del try_a_n_list[0]
        return s_set, a_n_set, nb_set, cur_profit, cur_budget, cur_w_list, pp_list

    def updatePersonalProbList(self, k_prod, i_node, cur_w_list, pp_list):
        prodprice = self.product_list[k_prod][2]
        if self.pp_strategy == -1:
            # -- buying products are independent --
            pp_list[k_prod][int(i_node)] = 0
        elif self.pp_strategy == 0:
            # -- a node can only buy a product --
            for k in range(self.num_product):
                pp_list[k][int(i_node)] = 0
        elif self.pp_strategy == 1:
            # -- after buying a product, the prob. to buy another product will decrease randomly --
            for k in range(self.num_product):
                if k == k_prod:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] = round(random.uniform(0, pp_list[k][int(i_node)]), 4)
        elif self.pp_strategy == 2:
            # -- choose as expensive as possible --
            for k in range(self.num_product):
                if k == k_prod:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] = round((prodprice / cur_w_list[int(i_node)]), 4)
        elif self.pp_strategy == 3:
            # -- choose as cheap as possible --
            for k in range(self.num_product):
                if k == k_prod:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] = round(1 - (prodprice / cur_w_list[int(i_node)]), 4)

        minprice = 1.0
        for k in range(self.num_product):
            minprice = min(minprice, self.product_list[k][2])
        for i in range(self.num_node):
            if cur_w_list[i] < minprice:
                for k in range(self.num_product):
                    pp_list[k][i] = 0.0
        return pp_list

    def updateProfitList(self, k_prod, ep_list, nb_set, a_n_set, cur_w_list, pp_list):
        mngic = ModelNGIC(self.graph_dict, self.seedcost_dict, self.product_list, self.total_budget, self.pp_strategy,
                          self.whether_infect_not_only_buying)
        for i in nb_set[k_prod]:
            ep_list[k_prod][int(i)] = mngic.getSeedExpectProfit(k_prod, i, a_n_set[k_prod], cur_w_list, pp_list[k_prod])
        return ep_list

if __name__ == "__main__":
    ### whether_infect_not_only_buying: (bool) if infect when only after buying, then False
    data_name = "email"
    product_name = "prod_r1p3n1"
    total_budget = 1
    iteration_times = 10
    pp_strategy = 1
    whether_infect_not_only_buying = bool(0)

    iniG = IniGraph(data_name)
    iniP = IniProduct()

    ### product_list: (list) [profit, cost, price]
    ### wallet_list: (list) the list of node's personal budget (wallet)
    ### wallet_list[i]: (float2) the i's wallet
    graph_dict = iniG.constructGraphDict()
    seedcost_dict = iniG.constructSeedCostDict()
    product_list, sum_price = iniP.getProductlist(product_name)
    wallet_list = iniG.getWalletList(product_name)
    num_node = len(seedcost_dict)
    num_product = len(product_list)

    mngic = ModelNGIC(graph_dict, seedcost_dict, product_list, total_budget, pp_strategy,
                      whether_infect_not_only_buying)
    result, avg_pro, avg_bud = [], 0.0, 0.0

    ### personal_prob_list: (list) the list of personal prob. for all combinations of nodes and products
    ### personal_prob_list[k]: (list) the list of personal prob. for k-product
    ### personal_prob_list[k][i]: (float2) the personal prob. for i-node for k-product
    now_profit, now_budget = 0.0, 0.0
    seed_set, activated_node_set, nban_set = [set() for _ in range(num_product)], [set() for _ in range(num_product)], [set(graph_dict.keys()) for _ in range(num_product)]
    personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]
    current_wallet_list = wallet_list.copy()

    start_time = time.time()

    print("calAllSeedProfit")
    all_profit_list = mngic.calAllSeedProfit(wallet_list)
    expect_profit_list = all_profit_list.copy()
    pro_k_list, bud_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]
    print("getMostValuableSeed")
    mep, nban_set = mngic.getMostValuableSeed(expect_profit_list, nban_set, now_budget)

    # -- main --
    while now_budget < total_budget and mep[2] != '-1':
        print("addSeedIntoSeedSet")
        seed_set, activated_node_set, nban_set, current_k_profit, current_k_budget, current_wallet_list, personal_prob_list = \
            mngic.addSeedIntoSeedSet(mep[1], mep[2], seed_set, activated_node_set, nban_set, current_wallet_list, personal_prob_list)
        pro_k_list[mep[1]] += current_k_profit
        bud_k_list[mep[1]] += current_k_budget
        now_profit += current_k_profit
        now_budget += current_k_budget
        print(pro_k_list, bud_k_list, now_profit, now_budget)
        print("updateProfitList")
        expect_profit_list = mngic.updateProfitList(mep[1], expect_profit_list, nban_set, activated_node_set, current_wallet_list, personal_prob_list)
        print("getMostValuableSeed")
        mep, nban_set = mngic.getMostValuableSeed(expect_profit_list, nban_set, now_budget)
        # print(mep[1], mep[2], round(current_profit, 4), round(current_budget, 4), seed_set)

    print("result")
    result.append([round(now_profit, 4), round(now_budget, 4), seed_set])
    avg_pro += now_profit
    avg_bud += now_budget

    how_long = round(time.time() - start_time, 4)
    print(result)
    print(avg_pro, avg_bud)
    print("total time: " + str(how_long) + "sec")
