import numpy as n
from functions import corr_max_data


# CALCULATE RISK ON A PORTFOLIO, GIVEN DATA
def total_risk(weights, csv_list):
    # INITIALIZE CORRELATION MATRIX
    all_corr = []
    # DIVIDE PERCENTS
    weights = [float(s)/100 for s in weights]
    # INITIALIZE STD LIST
    stds = []
    # FOR EACH CSV DATA
    for csv_data in csv_list:
        # APPEND STD
        stds.append(n.std(csv_data))
        # TO APPEND CORRELATIONS
        to_append = []
        # HALF THE CORR DATA WITH THIS TRICK
        for j in range(csv_list.index(csv_data) + 1, len(csv_list)):
            # GET CORR FOR I AND OTHER DATA
            to_append.append(corr_max_data(csv_data, csv_list[j]))
        # APPEND TO CORR
        all_corr.append(to_append)
    # POP
    all_corr.pop()
    # SET TOTAL RISK
    total_risk = 0
    # SET WEIGHTS
    stds_weights = n.multiply(n.square(stds), n.square(weights))
    # ADD THE STD TOO TOTAL
    for i in stds_weights:
        total_risk += i
    # ITERATE ON RANGE OF THE CORRELATIONS
    iterable = range(len(all_corr))
    # ITERATE THROUGH WEIGHTS AND STD LIST
    for i in iterable:
        # SET TO ADD
        to_add = 2 * stds[i] * weights[i]
        # SET COUNTER
        c = 0
        # ITERATE THROUGH THE REST OF THE LIST
        for j in range(iterable.index(i), len(all_corr)):
            # GET NEXT ITEM
            j += 1
            # MULTIPLY THE WEIGHTS AND RISK
            to_add = to_add * stds[j] * weights[j]
            # MULTIPLY THE CORRELATION
            to_add *= all_corr[i][c]
            # ITERATE COUNTER
            c += 1
            # ADD TO TOTAL
            total_risk += to_add
    # GET SQUARE ROOT OF THE TOTAL RISK
    total_risk = n.sqrt(n.abs(total_risk))
    return total_risk
