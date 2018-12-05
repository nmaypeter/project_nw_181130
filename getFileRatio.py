for pps in range(1, 4):
    for setting in range(1, 9):
        if setting == 1:
            data_name = "email"
            product_name = "prod_r1p3n1"
            num_ratio, num_price = 1, 3
        elif setting == 2:
            data_name = "email"
            product_name = "prod_r1p3n2"
            num_ratio, num_price = 1, 3
        elif setting == 3:
            data_name = "email"
            product_name = "prod_r1p4n1"
            num_ratio, num_price = 1, 4
        elif setting == 4:
            data_name = "email"
            product_name = "prod_r1p4n2"
            num_ratio, num_price = 1, 4
        elif setting == 5:
            data_name = "email"
            product_name = "prod_r1p5n1"
            num_ratio, num_price = 1, 5
        elif setting == 6:
            data_name = "email"
            product_name = "prod_r1p5n2"
            num_ratio, num_price = 1, 5
        elif setting == 7:
            data_name = "email"
            product_name = "prod_r2p2n1"
            num_ratio, num_price = 2, 2
        elif setting == 8:
            data_name = "email"
            product_name = "prod_r2p2n2"
            num_ratio, num_price = 2, 2
        num_product = num_ratio * num_price
        result_pro, result_cost = [[] for _ in range(num_product)], [[] for _ in range(num_product)]
        for total_budget in range(1, 11):
            try:
                result_name = "result/mngic_pps" + str(pps) + "/" + data_name + "_" + product_name + "/" + data_name + "_" + product_name + "_b" + str(total_budget) + "_i100.txt"
                lnum = 0
                with open(result_name) as f:
                    for line in f:
                        lnum += 1
                        if lnum <= 6:
                            continue
                        elif lnum == 7:
                            (l) = line.split()
                            for nl in range(2, len(l)):
                                result_pro[nl-2].append(l[nl])
                        elif lnum == 8:
                            (l) = line.split()
                            for nl in range(2, len(l)):
                                result_cost[nl-2].append(l[nl])
                        else:
                            break
                f.close()
            except FileNotFoundError:
                continue

        fw = open("result/mngic_pps" + str(pps) + "/" + data_name + "_" + product_name + "_ratio_pro.txt", 'w')
        for line in result_pro:
            for l in line:
                fw.write(str(l) + "\t")
            fw.write("\n")
        fw.close()
        fw = open("result/mngic_pps" + str(pps) + "/" + data_name + "_" + product_name + "_ratio_cost.txt", 'w')
        for line in result_cost:
            for l in line:
                fw.write(str(l) + "\t")
            fw.write("\n")
        fw.close()