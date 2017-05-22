import pysal
import math
import csv
import numpy as np

from pysal.weights.weights import WSP, WSP2W
from pysal.spreg.ml_error import ML_Error
from pysal.spreg.ml_lag import ML_Lag

from scipy.sparse import csc_matrix

from aggregator import AGGREGATED_FILE_NAME
from helpers import (
    create_square,
    get_mid_point,
    categories_prefixes,
    category_subfields,
    configure_logger,
    ensure_dir,
)



log = configure_logger(__name__)
REGION_BANDWIDTH = 0.15
WEIGHT_MATRIX_FILE_NAME = 'weights.gal'


def get_weight(distance, venue_counts_index, power=2):
    return 0 if distance > REGION_BANDWIDTH * (1 + venue_counts_index) else (
        math.pow((
            1 - math.pow(
                max(distance - REGION_BANDWIDTH * venue_counts_index, 0)
                / REGION_BANDWIDTH, power
            )
        ), power)
    )


def calculate_venue_quantity_index(row, all_quantities):
    index = 0
    for key, i in zip(
            categories_prefixes,
            range(6, len(row), len(category_subfields))
    ):
        index += row[i] / all_quantities.get(key)
    return index / len(all_quantities.items())


def calculate_locations_venues_count_index(loc1_index, loc2_index, power=2):
    return math.pow(math.fabs(loc1_index - loc2_index), 1 / power)


def calculate_distance(loc1, loc2):
    mid_point1_lat, mid_point1_long = get_mid_point(loc1, is_str=False)
    mid_point2_lat, mid_point2_long = get_mid_point(loc2, is_str=False)
    return math.sqrt(
        math.pow(mid_point1_lat - mid_point2_lat, 2) +
        math.pow(mid_point1_long - mid_point2_long, 2)
    )


def make_weights():
    log.debug('Opening aggregated data from {}'.format(AGGREGATED_FILE_NAME))
    db = pysal.open(AGGREGATED_FILE_NAME)
    fields_num = len(db.header)
    db_size = len(db)
    dist_matr = []
    log.debug('Constructing venues counts by categories')
    counts_by_category = {key: 0 for key in categories_prefixes}
    for row in range(db_size):
        for key, index in zip(
            categories_prefixes,
            range(6, fields_num, len(category_subfields))
        ):
            counts_by_category[key] += db[row][0][index]
    log.debug('Is going to calculate elements of weight matrix')
    for reg_row in db:
        location_row = create_square(*reg_row[1:5])
        loc_row_index = calculate_venue_quantity_index(reg_row, counts_by_category)
        dist_row = []
        for col in range(db_size):
            reg_col = db[col][0]
            distance = calculate_distance(
                location_row,
                create_square(*reg_col[1:5])
            )
            loc_col_index = calculate_venue_quantity_index(
                reg_col, counts_by_category
            )
            row_col_index = calculate_locations_venues_count_index(
                loc_row_index, loc_col_index,
            )
            weight = get_weight(distance, row_col_index) if len(dist_matr) != len(dist_row) else 0
            log.debug('Weight for elements {} and {} is: {}'.format(
                len(dist_matr), len(dist_row), weight,
            ))
            dist_row.append(weight)
        dist_matr.append(dist_row)
    with open('weights_all.csv', 'w') as f:
        writer = csv.writer(f)
        for row in dist_matr:
            writer.writerow(row)

    log.info('Going to build PYSAL weight matrix.')
    wsp_matrix = WSP(csc_matrix(dist_matr))
    gal_format = pysal.open(WEIGHT_MATRIX_FILE_NAME, 'w')
    gal_format.write(WSP2W(wsp_matrix))
    gal_format.close()
    return WSP2W(wsp_matrix)


def get_weight_from_file():
    w_file = pysal.open(WEIGHT_MATRIX_FILE_NAME)
    return w_file.read()


def get_variable_vector(category='all'):
    data_file = pysal.open(AGGREGATED_FILE_NAME, 'r')
    col_name = '{}_count'.format(category)
    return np.array(data_file.by_col(col_name))


def get_matrix_x(category='all'):
    data_file = pysal.open(AGGREGATED_FILE_NAME)
    x = []
    for field in category_subfields[1:]:
        x.append(data_file.by_col('{}_{}'.format(category, field)))

    if category == 'all':
        return np.array(x).T

    x_np = np.array(x).T
    x_all = []
    for field in category_subfields[1:]:
        x_all.append(data_file.by_col('all_{}'.format(field)))

    x_all_np = np.array(x_all).T
    x_all_without_cat_np = x_all_np - x_np
    return np.hstack((x_np, x_all_without_cat_np))


def calculate_gamma_index(category):
    w = get_weight_from_file()
    y = get_variable_vector(category)
    g = pysal.Gamma(y, w)
    ensure_dir('estimation_results/')
    directory = 'estimation_results/gamma'
    ensure_dir(directory)
    with open('{}/{}.csv'.format(directory, category), 'w') as res_file:
        writer = csv.writer(res_file)
        writer.writerow([g.g])
        writer.writerow([g.sim_g])
        writer.writerow([g.p_sim_g])
        writer.writerow([g.mean_g])
        writer.writerow([g.min_g])
        writer.writerow([g.max_g])
    print(g.g)
    print("%.3f"%g.g_z)
    print(g.p_sim_g)
    print(g.min_g)
    print(g.max_g)
    print(g.mean_g)


def calculate_join_count_statistics(category):
    w = get_weight_from_file()
    y = get_variable_vector(category)
    jc = pysal.Join_Counts(y, w)
    ensure_dir('estimation_results/')
    directory = 'estimation_results/join_count_statistics'
    ensure_dir(directory)
    with open('{}/{}.csv'.format(directory, category), 'w') as res_file:
        writer = csv.writer(res_file)
        writer.writerow([jc.bb])
        writer.writerow([jc.ww])
        writer.writerow([jc.bw])
        writer.writerow([jc.J])
    print(jc.bb)
    print(jc.bw)
    print(jc.ww)
    print(jc.J)


def calculate_moran_i(category):
    w = get_weight_from_file()
    y = get_variable_vector(category)
    mi = pysal.Moran(y, w)
    ensure_dir('estimation_results/')
    directory = 'estimation_results/moran'
    ensure_dir(directory)
    with open('{}/{}.csv'.format(directory, category), 'w') as res_file:
        writer = csv.writer(res_file)
        writer.writerow([mi.I])
        writer.writerow([mi.EI])
        writer.writerow([mi.VI_norm])
        writer.writerow([mi.seI_norm])
        writer.writerow([mi.z_norm])
        writer.writerow([mi.p_norm])
    print("%.3f" % mi.I)
    print(mi.EI)
    print("%.3f" % mi.z_norm)
    print("%.5f" % mi.p_norm)
    print(mi.p_sim)
    np.random.seed(10)
    mir = pysal.Moran(y, w, permutations=9999)
    print(mir.p_sim)


def calculate_geary_c(category):
    w = get_weight_from_file()
    y = get_variable_vector(category)
    gc = pysal.Geary(y, w)
    ensure_dir('estimation_results/')
    directory = 'estimation_results/geary_c'
    ensure_dir(directory)
    with open('{}/{}.csv'.format(directory, category), 'w') as res_file:
        writer = csv.writer(res_file)
        writer.writerow([gc.C])
        writer.writerow([gc.EC])
        writer.writerow([gc.VC_norm])
        writer.writerow([gc.z_norm])
        writer.writerow([gc.p_norm])
    print("%.3f" % gc.C)
    print(gc.EC)
    print("%.3f" % gc.z_norm)
    print(gc.p_sim)


def calculate_local_moran(category):
    w = get_weight_from_file()
    y = get_variable_vector(category)
    lm = pysal.Moran_Local(y, w)
    ensure_dir('estimation_results/')
    directory = 'estimation_results/moran_local'
    ensure_dir(directory)
    with open('{}/{}.csv'.format(directory, category), 'w') as res_file:
        writer = csv.writer(res_file)
        writer.writerow([lm.Is])
        writer.writerow([lm.q])
        writer.writerow([lm.p_sim])
        writer.writerow([lm.EI_sim])
        writer.writerow([lm.VI_sim])
        writer.writerow([lm.seI_sim])
        writer.writerow([lm.z_sim])
        writer.writerow([lm.p_z_sim])
    print(lm.p_sim)
    sig = lm.p_sim < 0.01
    print(lm.p_sim[sig])
    print(lm.q[sig])


def calculate_sem(category):
    w = get_weight_from_file()
    y = get_variable_vector(category)
    x = get_matrix_x(category)
    y.shape = (len(y), 1)
    ensure_dir('regression_results')
    directory = 'regression_results/sem/'
    ensure_dir(directory)
    d = ML_Error(y, x, w=w)
    with open('{}/{}.csv'.format(directory, category), 'w') as res_file:
        writer = csv.writer(res_file)
        writer.writerow(d.betas)
        writer.writerow([d.lam])
        writer.writerow(d.u)
        writer.writerow(d.e_filtered)
        writer.writerow(d.predy)
        writer.writerow(d.y)
        writer.writerow([d.mean_y])
        writer.writerow([d.std_y])
        writer.writerow([d.sig2])
        writer.writerow([d.logll])
        writer.writerow([d.aic])
        writer.writerow([d.schwarz])
        writer.writerow([d.pr2])
        writer.writerow([d.utu])
        writer.writerow(d.std_err)
        writer.writerow(d.z_stat)
    print(d.summary)


def base_sar(category, method='sar'):
    w = make_weights()
    y = get_variable_vector(category)
    x = get_matrix_x(category)
    y.shape = (len(y), 1)
    lag_x = pysal.lag_spatial(w, x)
    new_x = np.hstack((x, lag_x)) if method == 'durbin' else x
    d = ML_Lag(y, new_x, w=w, method='ord')
    ensure_dir('regression_results/')
    directory = 'regression_results/{}/'.format(method)
    ensure_dir(directory)
    with open('{}/{}.csv'.format(directory, category), 'w') as res_file:
        writer = csv.writer(res_file)
        writer.writerow(d.betas)
        writer.writerow([d.rho])
        writer.writerow(d.u)
        writer.writerow(d.predy)
        writer.writerow(d.y)
        writer.writerow([d.mean_y])
        writer.writerow([d.std_y])
        writer.writerow([d.sig2])
        writer.writerow([d.logll])
        writer.writerow([d.aic])
        writer.writerow([d.schwarz])
        writer.writerow(d.predy_e)
        writer.writerow(d.e_pred)
        writer.writerow([d.pr2])
        writer.writerow([d.pr2_e])
        writer.writerow([d.utu])
        writer.writerow(d.std_err)
        writer.writerow(d.z_stat)
    print(d.summary)


def calculate_sar(category):
    base_sar(category, method='sar')


def calculate_durbin(category):
    base_sar(category, method='durbin')
