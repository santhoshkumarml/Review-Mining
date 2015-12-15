import collections
import datetime
import os, math, random

import matplotlib.pyplot as plt
import networkx as nx
import nltk
import numpy

import AppUtil
from itunes_utils.ItunesDataReader import ItunesDataReader
from util import GraphUtil, SIAUtil

nltk.data.path.append('/media/santhosh/Data/workspace/nltk_data')


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{v:d}'.format(p=pct, v=val)
    return my_autopct

def plotSuspiciousNessGraph(non_singleton_usr_suspicousness,
                            non_singleton_usr_non_suspicousness,
                            imgFolder, time_key_to_date_time,
                            title='Suspicious Non Singleton User',
                            plot_non_suspicious=False):
    fig = plt.figure(figsize=(24, 16))
    imgFile = os.path.join(imgFolder, title + '.png')

    g = nx.Graph()
    bnss_nodes = set()
    usr_nodes = set()

    node_labels = dict()

    for usrId in non_singleton_usr_suspicousness.keys():
        for revw_for_usr in non_singleton_usr_suspicousness[usrId]:
            bnss_id_for_revw = revw_for_usr.getBusinessID()
            date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)

            time_id_for_date_time = findTimeIdForDateTime(time_key_to_date_time,\
                                                          date_time_for_this_usr)
            bnss_nodes.add(bnss_id_for_revw)
            g.add_edge(usrId, bnss_id_for_revw, {'edge': (revw_for_usr.getRating(), time_id_for_date_time)})

            node_labels[bnss_id_for_revw] = bnss_id_for_revw
            usr_nodes.add(usrId)
            node_labels[usrId] = usrId

    if plot_non_suspicious:
        for usrId in non_singleton_usr_non_suspicousness.keys():
            for revw_for_usr in non_singleton_usr_non_suspicousness[usrId]:
                bnss_id_for_revw = revw_for_usr.getBusinessID()
                date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)

                time_id_for_date_time = findTimeIdForDateTime(time_key_to_date_time,\
                                                              date_time_for_this_usr)
                bnss_nodes.add(bnss_id_for_revw)
                g.add_edge(usrId, bnss_id_for_revw, {'edge': (revw_for_usr.getRating(),
                                                               time_id_for_date_time)})
                node_labels[bnss_id_for_revw] = bnss_id_for_revw
                usr_nodes.add(usrId)
                node_labels[usrId] = usrId

    edge_labels=dict([((u,v,),d['edge'])
             for u,v,d in g.edges(data=True)])

    pos = dict()
    i = 0
    for node in usr_nodes:
        pos[node] = (1, i)
        i += 3

    i = 0
    for node in bnss_nodes:
        pos[node] = (4, i)
        i += 3

    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(usr_nodes),
                           node_color='b',
                           node_size=500,
                           alpha=0.8)
    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(bnss_nodes),
                           node_color='m',
                           node_size=500,
                           alpha=0.8)

    nx.draw_networkx_edges(g, pos,
                       edgelist=[(usrId, revw_for_usr.getBusinessID())
                                 for usrId in non_singleton_usr_suspicousness.keys()
                                 for revw_for_usr in non_singleton_usr_suspicousness[usrId]],
                       alpha=0.5, edge_color='r')

    if plot_non_suspicious:
        nx.draw_networkx_edges(g, pos,
                               edgelist=[(usrId, revw_for_usr.getBusinessID())
                                         for usrId in non_singleton_usr_non_suspicousness.keys()
                                         for revw_for_usr in non_singleton_usr_non_suspicousness[usrId]],
                               alpha=0.5, edge_color='g')

    nx.draw_networkx_labels(g, pos, labels=node_labels)
    # nx.draw_networkx_edges(g, pos, width=1.0, alpha=0.5)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels,\
                                 label_pos= 0.3)

    plt.title(title)
    plt.axis('off')
    plt.savefig(imgFile)
    # plt.show()
    plt.close()


def plotRatingDistribution(review_rating_distribution, imgFolder,
                           title='Rating Distribution'):
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes([0.1, 0.1, 0.8, 0.8])
    imgFile = os.path.join(imgFolder, title + '.png')
    labels = review_rating_distribution.keys()
    fracs = review_rating_distribution.values()

    ax.pie(fracs, labels=labels,
        autopct=make_autopct(fracs), shadow=False, startangle=90)
    plt.title(title, bbox={'facecolor': '0.8', 'pad': 5})
    plt.legend()
    plt.savefig(imgFile, bbox_inches='tight')
    plt.close()


def plotExtremityForNonSingletonUsr(extreme_usrs, non_extreme_usrs, imgFolder,
                                    title='Extremity of Non SingletonUsr'):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)
    width = 0.20
    imgFile = os.path.join(imgFolder, title + '.png')
    x_labels = ['Extreme Users', 'Non Extreme Users']
    p_extreme = ax.bar(0, extreme_usrs, width, color='r')
    p_non_extreme = ax.bar(0.5, non_extreme_usrs, width, color='b')

    plt.ylabel('Count')
    plt.title(title)
    plt.xticks([0.10, 0.60], x_labels)
    plt.legend()
    plt.savefig(imgFile, bbox_inches='tight')
    plt.close()


def plotReviewTimeRating(review_time_rating, imgFolder, title='Time Wise Rating Count'):
    fig = plt.figure(figsize=(36, 10))
    ax = fig.add_subplot(1, 1, 1)
    imgFile = os.path.join(imgFolder, title + '.png')
    colors = ['y', 'c', 'm', 'b', 'r']
    total_days = len(review_time_rating[1.0].keys())
    ind = numpy.arange(0, total_days*2, 2)
    width = 1.5
    x_labels = [d.strftime('%m/%d') for d in sorted(review_time_rating[1.0].keys())]
    pS = []
    btm = None
    colr = 0
    for rating_key in sorted(review_time_rating.keys()):
        val = review_time_rating[rating_key]
        od = collections.OrderedDict(sorted(val.items()))
        val = numpy.array(od.values())
        if btm is None:
            p = ax.bar(ind, val, width, color=colors[colr])
            btm = val
        else:
            p = ax.bar(ind, val, width, color=colors[colr], bottom=btm)
            btm = numpy.array([btm[i] + val[i] for i in range(0, total_days)])

        colr += 1
        pS.append(p)

    plt.ylabel(title)
    plt.title(title)
    plt.xticks(ind + width/2., x_labels)
    plt.legend([p[0] for p in pS], range(1, 6))
    plt.savefig(imgFile, bbox_inches='tight')
    plt.close()


def getNecessaryDs(csvFolder, rdr=ItunesDataReader(), readReviewsText=False, timeLength='1-W'):
    suspicious_timestamps = dict()
    suspicious_timestamp_ordered = list()
    with open(os.path.join(csvFolder, 'out_all_features_mul_reviews.log')) as f:
        lines = f.readlines()
        for line in lines:
            bnss_key, idx1, idx2, score = line.strip().split()
            idx1 = int(idx1[1:-1])
            idx2 = int(idx2[:-1])
            if bnss_key not in suspicious_timestamps:
                suspicious_timestamps[bnss_key] = set()
            for idx in range(idx1, idx2):
                suspicious_timestamps[bnss_key].add(idx)
            suspicious_timestamp_ordered.append((bnss_key, (idx1, idx2)))
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = AppUtil.readData(csvFolder,
                                                                            readReviewsText=readReviewsText, rdr=rdr)
    ctg = GraphUtil.createTemporalGraph(usrIdToUserDict,
                                        bnssIdToBusinessDict,
                                        reviewIdToReviewsDict,
                                        timeLength)
    superGraph = GraphUtil.createSuperGraph(usrIdToUserDict, bnssIdToBusinessDict,
                                            reviewIdToReviewsDict, timeLength)
    time_key_to_date_time = dict()
    for t_k in ctg.keys():
        d = ctg[t_k].getDateTime()
        time_key_to_date_time[t_k] = d

    # del time_key_to_date_time, suspicious_timestamps, superGraph, ctg

    return ctg, superGraph, time_key_to_date_time, suspicious_timestamps, suspicious_timestamp_ordered


def plotAllStats(time_wise_non_singleton_usr_suspicousness,\
                  time_wise_non_singleton_usr_non_suspicousness,\
                  time_wise_four_grams_dict,\
                  time_wise_three_grams_dict, time_wise_two_grams_dict,\
                  time_wise_all_user_review_rating_distribution,\
                  time_wise_singleton_review_rating_distribution,\
                  time_wise_non_singleton_review_rating_distribution,\
                  time_wise_extreme_non_singleton_usrs,\
                  time_wise_non_extreme_non_singleton_usrs,\
                  time_wise_review_time_rating,\
                  time_key_start, time_key_end, time_key_to_date_time,\
                  bnssImgFolder):
    for time_key in range(time_key_start, time_key_end):
        imgFolder = os.path.join(bnssImgFolder, str(time_key))
        if not os.path.exists(imgFolder):
                os.makedirs(imgFolder)
        all_user_review_rating_distribution = time_wise_all_user_review_rating_distribution[time_key]
        singleton_review_rating_distribution = time_wise_non_singleton_review_rating_distribution[time_key]
        non_singleton_review_rating_distribution = time_wise_non_singleton_review_rating_distribution[time_key]
        extreme_non_singleton_usrs, non_extreme_non_singleton_usrs = time_wise_extreme_non_singleton_usrs[time_key], time_wise_non_extreme_non_singleton_usrs[time_key]
        non_singleton_usr_suspicousness, non_singleton_usr_non_suspicousness = time_wise_non_singleton_usr_suspicousness[time_key], time_wise_non_singleton_usr_non_suspicousness[time_key]
        plotRatingDistribution(all_user_review_rating_distribution, imgFolder, title='All Review Rating Count')
        plotRatingDistribution(singleton_review_rating_distribution, imgFolder, title='Singleton Review Rating Count')
        plotRatingDistribution(non_singleton_review_rating_distribution, imgFolder,
                               title='Non Singleton Review Rating Count')
        plotExtremityForNonSingletonUsr(extreme_non_singleton_usrs, non_extreme_non_singleton_usrs, imgFolder)
        plotSuspiciousNessGraph(non_singleton_usr_suspicousness, non_singleton_usr_non_suspicousness,
                                imgFolder, time_key_to_date_time, plot_non_suspicious=False)
    plotReviewTimeRating(time_wise_review_time_rating, bnssImgFolder)


def findTimeIdForDateTime(time_key_to_date_time, date_time_for_this_usr):
    time_id_for_date_time = -1
    for time_id in time_key_to_date_time.keys():
        if date_time_for_this_usr < time_key_to_date_time[time_id].date():
            break
        time_id_for_date_time = time_id
    return time_id_for_date_time


def printNGrams(time_key_start, time_key_end, time_wise_four_grams_dict,\
                time_wise_three_grams_dict, time_wise_two_grams_dict):
    for time_key in range(time_key_start, time_key_end):
        two_grams_dict = time_wise_two_grams_dict[time_key]
        three_grams_dict = time_wise_three_grams_dict[time_key]
        four_grams_dict = time_wise_four_grams_dict[time_key]
        print '------------------------', time_key, '----------------------------------------'
        print 'Two Grams'
        print sorted(two_grams_dict.iteritems(), key=lambda (gram, count):count, reverse=True)
        print 'Three Grams'
        print sorted(three_grams_dict.iteritems(), key=lambda (gram, count):count, reverse=True)
        print 'Four Grams'
        print sorted(four_grams_dict.iteritems(), key=lambda (gram, count):count, reverse=True)
        print '------------------------', time_key, '----------------------------------------'

def findStatsForEverything(plotDir,  bnssKey, time_key_wdw, necessaryDs, readReviewsText=False, doPlot=False):
    ctg, superGraph, time_key_to_date_time,\
     suspicious_timestamps, suspicious_timestamp_ordered = necessaryDs

    time_key_start, time_key_end = time_key_wdw

    time_wise_non_singleton_usr_suspicousness = {key: dict()\
                                                  for key in range(time_key_start, time_key_end)}
    time_wise_non_singleton_usr_non_suspicousness = {key: dict()\
                                                  for key in range(time_key_start, time_key_end)}
    time_wise_four_grams_dict = {key: dict()\
                                 for key in range(time_key_start, time_key_end)}
    time_wise_three_grams_dict = {key: dict()\
                                 for key in range(time_key_start, time_key_end)}
    time_wise_two_grams_dict = {key: dict()\
                                 for key in range(time_key_start, time_key_end)}

    time_wise_all_user_review_rating_distribution = {key:{float(key): 0.0 for key in range(1, 6)}\
                                                      for key in range(time_key_start, time_key_end)}
    time_wise_singleton_review_rating_distribution = {key:{float(key): 0.0 for key in range(1, 6)}\
                                                      for key in range(time_key_start, time_key_end)}
    time_wise_non_singleton_review_rating_distribution = {key:{float(key): 0.0 for key in range(1, 6)}\
                                                      for key in range(time_key_start, time_key_end)}

    time_wise_extreme_non_singleton_usrs = {key: 0\
                                 for key in range(time_key_start, time_key_end)}
    time_wise_non_extreme_non_singleton_usrs = {key: 0\
                                 for key in range(time_key_start, time_key_end)}

    time_wise_review_time_rating = {float(key): {(time_key_to_date_time[time_key]\
                                                 + datetime.timedelta(days=day_inc)).date(): 0.0\
                                                 for time_key in range(time_key_start, time_key_end)
                                                 for day_inc in range(0, 7)}
                                               for key in range(1, 6)}

    def put_grams(grams, grams_dict):
        for gram in grams:
            if gram not in grams_dict:
                grams_dict[gram] = 0.0
            grams_dict[gram] += 1.0

    for time_key in range(time_key_start, time_key_end):
        G = ctg[time_key]
        if (bnssKey, SIAUtil.PRODUCT) not in G:
            continue
        neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
        all_usrs = set([usrId for usrId, usr_type in neighboring_usr_nodes])
        singleton_usrs = set([usrId for usrId, usr_type in neighboring_usr_nodes
                      if len(superGraph.neighbors((usrId, usr_type))) == 1])
        non_singleton_usrs = all_usrs - singleton_usrs

        non_singleton_usr_suspicousness = time_wise_non_singleton_usr_suspicousness[time_key]
        non_singleton_usr_non_suspicousness = time_wise_non_singleton_usr_non_suspicousness[time_key]
        non_singleton_usr_all_review_distribution = dict()

        for non_singleton_usr in non_singleton_usrs:
            reviews_for_this_usr = sorted([superGraph.getReview(non_singleton_usr, bnssId) for (bnssId, bnss_type)
                                           in superGraph.neighbors((non_singleton_usr, SIAUtil.USER))])

            non_singleton_usr_all_review_distribution[non_singleton_usr] = {float(key): 0.0 for key in range(1, 6)}

            non_singleton_usr_suspicousness[non_singleton_usr] = list()

            non_singleton_usr_non_suspicousness[non_singleton_usr] = list()

            for revw_for_usr in reviews_for_this_usr:
                bnssId_for_this_review = revw_for_usr.getBusinessID()

                if bnssKey == bnssId_for_this_review:
                    continue

                non_singleton_usr_all_review_distribution[non_singleton_usr][revw_for_usr.getRating()] += 1.0

                date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)

                time_id_for_date_time = findTimeIdForDateTime(time_key_to_date_time,\
                                                              date_time_for_this_usr)
                if bnssId_for_this_review in suspicious_timestamps and \
                                time_id_for_date_time in suspicious_timestamps[bnssId_for_this_review]:
                    non_singleton_usr_suspicousness[non_singleton_usr].append(revw_for_usr)
                else:
                    non_singleton_usr_non_suspicousness[non_singleton_usr].append(
                        revw_for_usr)

        reviews_for_bnss_in_time_key = sorted([G.getReview(usrId, bnssKey) for (usrId, usr_type)
                                               in neighboring_usr_nodes],
                                              key=lambda r: SIAUtil.getDateForReview(r))

        four_grams_dict = time_wise_four_grams_dict[time_key]
        three_grams_dict = time_wise_three_grams_dict[time_key]
        two_grams_dict = time_wise_two_grams_dict[time_key]

        all_user_review_rating_distribution = time_wise_all_user_review_rating_distribution[time_key]
        singleton_review_rating_distribution = time_wise_singleton_review_rating_distribution[time_key]
        non_singleton_review_rating_distribution = time_wise_non_singleton_review_rating_distribution[time_key]

        for r in reviews_for_bnss_in_time_key:
            if readReviewsText:
                decoded_text = r.getReviewText().decode('UTF-8')
                two_grams = nltk.ngrams(nltk.word_tokenize(decoded_text), 2)
                three_grams = nltk.ngrams(nltk.word_tokenize(decoded_text), 3)
                four_grams = nltk.ngrams(nltk.word_tokenize(decoded_text), 4)

                put_grams(two_grams, two_grams_dict)
                put_grams(three_grams, three_grams_dict)
                put_grams(four_grams, four_grams_dict)

            all_user_review_rating_distribution[r.getRating()] += 1.0
            if r.getUserId() in singleton_usrs:
                singleton_review_rating_distribution[r.getRating()] += 1.0
            else:
                non_singleton_review_rating_distribution[r.getRating()] += 1.0
            date_of_review = SIAUtil.getDateForReview(r)
            time_wise_review_time_rating[r.getRating()][date_of_review] += 1.0


        total_non_singleton_usrs = len(non_singleton_usrs)
        extreme_non_singleton_usrs = 0


        for usrId in non_singleton_usrs:
            rating_dist = non_singleton_usr_all_review_distribution[usrId]
            if rating_dist[2.0] == 0 and rating_dist[3.0] == 0 and rating_dist[4.0] == 0:
                extreme_non_singleton_usrs += 1
        non_extreme_non_singleton_usrs = total_non_singleton_usrs - extreme_non_singleton_usrs
        time_wise_extreme_non_singleton_usrs[time_key] = extreme_non_singleton_usrs
        time_wise_non_extreme_non_singleton_usrs[time_key] = non_extreme_non_singleton_usrs

    if readReviewsText:
        printNGrams(time_key_start, time_key_end, time_wise_four_grams_dict,\
                    time_wise_three_grams_dict, time_wise_two_grams_dict)

    if doPlot:
        bnssImgFolder = os.path.join(plotDir, bnssKey + '_' + str(time_key_start)\
                                     + '_' + str(time_key_end))
        plotAllStats(time_wise_non_singleton_usr_suspicousness,\
                     time_wise_non_singleton_usr_non_suspicousness,\
                     time_wise_four_grams_dict, time_wise_three_grams_dict,\
                     time_wise_two_grams_dict,\
                     time_wise_all_user_review_rating_distribution,\
                     time_wise_singleton_review_rating_distribution,\
                     time_wise_non_singleton_review_rating_distribution,\
                     time_wise_extreme_non_singleton_usrs,\
                     time_wise_non_extreme_non_singleton_usrs,\
                     time_wise_review_time_rating,\
                     time_key_start, time_key_end, time_key_to_date_time,\
                     bnssImgFolder)
