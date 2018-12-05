from Model_NaiveGreedyIC import *

class ModelHD():
    def __init__(self, graph_dict, seedcost_dict, product_list, total_budget, pp_strategy,
                 whether_infect_not_only_buying):
        self.graph_dict = graph_dict
        self.seedcost_dict = seedcost_dict
        self.product_list = product_list
        self.total_budget = total_budget
        self.num_node = len(seedcost_dict)
        self.num_product = len(product_list)
        self.diffusion_threshold = 0.01
        self.pp_strategy = pp_strategy
        self.whether_infect_not_only_buying = whether_infect_not_only_buying

    def constructDegreeDict(self, data_name):
        with open(IniGraph(data_name).data_degree_path) as f:
            degree_list = []
            for line in f:
                (node, degree) = line.split()
                degree_list.append([node, degree])
            degree_list.sort(key=sortSecond, reverse=True)
            degree_dict = {}
            for i_node, i_deg in degree_list:
                if i_deg in degree_dict:
                    degree_dict[i_deg].add(i_node)
                else:
                    degree_dict[i_deg] = {i_node}
        return degree_dict

    def getHighDegreeSet(self, d_dict):
        while d_dict[max(d_dict)] == set():
            if d_dict[max(d_dict)] == set():
                del d_dict[max(d_dict)]
            if d_dict == set():
                return {}
        return d_dict[max(d_dict)]

    def calHighDegreeSeedProfit(self, hd_set, a_n_set, nb_set, cur_w_list, pp_list):
        # -- calculate expected profit for all combinations of nodes and products --
        ### expect_profit_list: (list) the list of expected profit for all combinations of nodes and products
        ### expect_profit_list[k]: (list) the list of expected profit for k-product
        ### expect_profit_list[k][i]: (float4) the expected profit for i-node for k-product
        expect_profit_list = []
        for num in range(self.num_product):
            expect_profit_list.append([])

        mngic = ModelNGIC(self.graph_dict, self.seedcost_dict, self.product_list, self.total_budget, self.pp_strategy,
                          self.whether_infect_not_only_buying)

        for k in range(self.num_product):
            for i in hd_set:
                if i not in self.graph_dict:
                    ep = self.product_list[k][0] - self.seedcost_dict[i]
                elif i in a_n_set[k]:
                    nb_set[k].remove(i)
                    ep = 0.0
                else:
                    ep = mngic.getSeedExpectProfit(k, i, a_n_set[k], cur_w_list, pp_list[k])
                expect_profit_list[k].append(ep)
        return expect_profit_list

if __name__ == "__main__":
    data_name = "email"
    product_name = "prod_r1p3n1"
    total_budget = 1
    iteration_times = 10
    pp_strategy = 1
    whether_infect_not_only_buying = bool(0)

    iniG = IniGraph(data_name)
    iniP = IniProduct()

    graph_dict = iniG.constructGraphDict()
    seedcost_dict = iniG.constructSeedCostDict()
    product_list, sum_price = iniP.getProductlist(product_name)
    wallet_list = iniG.getWalletList(product_name)
    num_node = len(seedcost_dict)
    num_product = len(product_list)

    mhd = ModelHD(graph_dict, seedcost_dict, product_list, total_budget, pp_strategy,
                  whether_infect_not_only_buying)
    result, avg_pro, avg_bud = [], 0.0, 0.0

    now_profit, now_budget = 0.0, 0.0
    seed_set, activated_node_set, nban_set = [set() for _ in range(num_product)], [set() for _ in range(num_product)], [set(graph_dict.keys()) for _ in range(num_product)]
    personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]
    current_wallet_list = wallet_list.copy()

    start_time = time.time()

    pro_k_list, bud_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]

    degree_dict = mhd.constructDegreeDict(data_name)
    high_degree_set = mhd.getHighDegreeSet(degree_dict)
    ep = mhd.calHighDegreeSeedProfit(high_degree_set, activated_node_set, nban_set, current_wallet_list, personal_prob_list)


