from Model_NaiveGreedyIC import *

if __name__ == "__main__":
    data_name, product_name = "", ""
    for setting in range(1, 2):
        # print("setting = " + str(setting))
        if setting == 1:
            data_name = "email"
            product_name = "prod_r1p3n1"
        elif setting == 2:
            data_name = "email"
            product_name = "prod_r1p3n2"
        elif setting == 3:
            data_name = "email"
            product_name = "prod_r1p4n1"
        elif setting == 4:
            data_name = "email"
            product_name = "prod_r1p4n2"
        elif setting == 5:
            data_name = "email"
            product_name = "prod_r1p5n1"
        elif setting == 6:
            data_name = "email"
            product_name = "prod_r1p5n2"
        elif setting == 7:
            data_name = "email"
            product_name = "prod_r2p2n1"
        elif setting == 8:
            data_name = "email"
            product_name = "prod_r2p2n2"
        total_budget = 2
        iteration_times, itertimes = 2, 1
        pp_strategy = 1

        iniG = IniGraph(data_name)
        iniP = IniProduct()

        graph_dict = iniG.constructGraphDict()
        seedcost_dict = iniG.constructSeedCostDict()
        product_list, sum_price = iniP.getProductlist(product_name)
        wallet_list = iniG.getWalletList(product_name)
        num_node = len(seedcost_dict)
        num_product = len(product_list)

        for winob in range(1):
            # print("winob = " + str(winob))
            whether_infect_not_only_buying = bool(winob)
            result_profit_list = [[] for _ in range(int(iteration_times / itertimes))]
            result_avgtime_list = [[] for _ in range(int(iteration_times / itertimes))]
            result_totaltime_list = [[] for _ in range(int(iteration_times / itertimes))]
            for bud in range(1, total_budget + 1):
                # print("bud = " + str(bud))
                start_time = time.time()
                pro_k_list, bud_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]
                avg_pro, avg_bud = 0.0, 0.0
                all_result, result_ss_list, result_ss_times_list, result_ss_profit_list = [], [], [], []

                mngic = ModelNGIC(graph_dict, seedcost_dict, product_list, bud, pp_strategy,
                                  whether_infect_not_only_buying)
                # print("calAllSeedProfit")
                all_profit_list = mngic.calAllSeedProfit(wallet_list)
                expect_profit_list = all_profit_list.copy()
                for times in range(iteration_times):
                    # print("times = " + str(times))
                    print("budget = " + str(bud) + ", iteration = " + str(times) + ", pp_strategy = " + str(pp_strategy) +
                          ", whether_infect_not_only_buying = " + str(whether_infect_not_only_buying))
                    now_profit, now_budget = 0.0, 0.0
                    seed_set, activated_node_set, nban_set = [set() for _ in range(num_product)], [set() for _ in range(num_product)], [set(graph_dict.keys()) for _ in range(num_product)]
                    personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]
                    current_wallet_list = wallet_list.copy()

                    mep, nban_set = mngic.getMostValuableSeed(expect_profit_list, nban_set, now_budget)
                    # print("getMostValuableSeed")

                    # -- main --
                    while now_budget < bud and mep[2] != '-1':
                        # print("addSeedIntoSeedSet")
                        seed_set, activated_node_set, nban_set, current_k_profit, current_k_budget, current_wallet_list, personal_prob_list = \
                            mngic.addSeedIntoSeedSet(mep[1], mep[2], seed_set, activated_node_set, nban_set, current_wallet_list, personal_prob_list)
                        pro_k_list[mep[1]] += current_k_profit
                        bud_k_list[mep[1]] += current_k_budget
                        now_profit += current_k_profit
                        now_budget += current_k_budget
                        # print(pro_k_list, bud_k_list, now_profit, now_budget)
                        # print("updateProfitList")
                        expect_profit_list = mngic.updateProfitList(mep[1], expect_profit_list, nban_set, activated_node_set, current_wallet_list, personal_prob_list)
                        # print("getMostValuableSeed")
                        mep, nban_set = mngic.getMostValuableSeed(expect_profit_list, nban_set, now_budget)

                    # print("result")
                    all_result.append([round(now_profit, 4), round(now_budget, 4), seed_set])
                    avg_pro += now_profit
                    avg_bud += now_budget

                    if seed_set in result_ss_list:
                        result_ss_times_list[result_ss_list.index(seed_set)] += 1
                        result_ss_profit_list[result_ss_list.index(seed_set)] += round(now_profit, 4)
                    else:
                        result_ss_list.append(seed_set)
                        result_ss_times_list.append(1)
                        result_ss_profit_list.append(round(now_profit, 4))
                    # print(result_ss_list, result_ss_times_list, result_ss_profit_list)

                    how_long = round(time.time() - start_time, 4)
                    print("total time: " + str(how_long) + "sec")
                    # print(all_result[times])
                    # print("avg_profit = " + str(round(avg_pro / (times+1), 4)) + ", avg_budget = " + str(round(avg_bud / (times+1), 4)))

                    if (times + 1) % itertimes == 0:
                        # print("output1")
                        fw = open("result/mngic_pps" + str(pp_strategy) + "_winob" * whether_infect_not_only_buying + "/" +
                                  data_name + "_" + product_name + "/" +
                                  data_name + "_" + product_name + "_b" + str(bud) + "_i" + str(times + 1) + ".txt", 'w')
                        fw.write("data = " + data_name + ", total_budget = " + str(bud) + ", iteration_times = " + str(times + 1) + "\n" +
                                 "whether_infect_not_only_buying = " + str(whether_infect_not_only_buying) + "\n" +
                                 "avg_profit_per_iteration = " + str(round(avg_pro / (times + 1), 4)) + "\n" +
                                 "avg_budget_per_iteration = " + str(round(avg_bud / (times + 1), 4)) + "\n" +
                                 "total time: " + str(how_long) + ", avg_time = " + str(round(how_long / (times + 1), 4)) + "\n")
                        fw.write("\nprofit ratio:")
                        for k in range(num_product):
                            fw.write(" " + str(round(pro_k_list[k] / (times + 1), 4)))
                        fw.write("\nbudget ratio:")
                        for k in range(num_product):
                            fw.write(" " + str(round(bud_k_list[k] / (times + 1), 4)))
                        mrss_times = max(result_ss_times_list)
                        fw.write("\n\nmost frequent times, avg profit, seed set\n")
                        fw.write(str(mrss_times) + " " + str(round(result_ss_profit_list[result_ss_times_list.index(mrss_times)] / mrss_times, 4))
                                 + " " + str(result_ss_list[result_ss_times_list.index(mrss_times)]) + "\n")

                        for t, r in enumerate(all_result):
                            fw.write("\n" + str(t) + " " + str(round(r[0], 4)) + " " + str(round(r[1], 4)) + " " + str(r[2]))
                        fw.close()

                        result_profit_list[int((times + 1) / itertimes) - 1].append(str(round(avg_pro / (times + 1), 4)) + "\t")
                        result_avgtime_list[int((times + 1) / itertimes) - 1].append(str(round(how_long / (times + 1), 4)) + "\t")
                        result_totaltime_list[int((times + 1) / itertimes) - 1].append(str(how_long) + "\t")

            # print("output2")
            fw = open("result/mngic_pps" + str(pp_strategy) + "_winob" * whether_infect_not_only_buying + "/" +
                      data_name + "_" + product_name + "_profit.txt", 'w')
            for line in result_profit_list:
                for l in line:
                    fw.write(str(l))
                fw.write("\n")
            fw.close()
            fw = open("result/mngic_pps" + str(pp_strategy) + "_winob" * whether_infect_not_only_buying + "/" +
                      data_name + "_" + product_name + "_avgtime.txt", 'w')
            for line in result_avgtime_list:
                for l in line:
                    fw.write(str(l))
                fw.write("\n")
            fw.close()
            fw = open("result/mngic_pps" + str(pp_strategy) + "_winob" * whether_infect_not_only_buying + "/" +
                      data_name + "_" + product_name + "_totaltime.txt", 'w')
            for line in result_totaltime_list:
                for l in line:
                    fw.write(str(l))
                fw.write("\n")
            fw.close()