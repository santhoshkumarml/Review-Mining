import os
import pickle

from statistics import business_statistics_generator
from tryout.testAlgos import readData, csvFolder, plotDir
from util import GraphUtil, SIAUtil, StatConstants


def serializeBnssStats(bnss_key, plotDir, statistics_for_bnss):
    bnss_file_name = os.path.join(plotDir, bnss_key)
    print 'Serializing to file', bnss_file_name
    if not os.path.exists(bnss_file_name):
        with open(bnss_file_name, 'w') as f:
            pickle.dump(statistics_for_bnss, f)


def deserializeBnssStats(bnss_key, statsDir):
    return pickle.load(open(os.path.join(statsDir, bnss_key)))


def readAndGenerateStatistics(csvFolder, plotDir, timeLength = '1-W'):
    # Read data
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = readData(csvFolder)
    # Construct Graphs
    superGraph, cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict, \
                                                           bnssIdToBusinessDict, \
                                                           reviewIdToReviewsDict, timeLength)
    if not os.path.exists(plotDir):
        os.makedirs(plotDir)
    bnssKeys = [bnss_key for bnss_key, bnss_type in superGraph.nodes() \
                if bnss_type == SIAUtil.PRODUCT]
    bnssKeys = sorted(bnssKeys, reverse=True, key=lambda x: len(superGraph.neighbors((x, SIAUtil.PRODUCT))))
    # bnssKeys = ['363590051']
    # bnssKeys = bnssKeys[:2]
    measuresToBeExtracted = [measure for measure in StatConstants.MEASURES \
                             if measure != StatConstants.MAX_TEXT_SIMILARITY and measure != StatConstants.TF_IDF]
    lead_signals = [measure for measure in measuresToBeExtracted if measure in StatConstants.MEASURE_LEAD_SIGNALS]
    measuresToBeExtracted = [measure for measure in set(lead_signals).union(set(measuresToBeExtracted))]
    return bnssKeys, cross_time_graphs, measuresToBeExtracted, superGraph


def doSerializeAllBnss(csvFolder, plotDir, timeLength = '1-W'):
    bnssKeys, cross_time_graphs, measuresToBeExtracted, superGraph = readAndGenerateStatistics(csvFolder, plotDir)
    for bnssKey in bnssKeys:
        statistics_for_bnss = business_statistics_generator.extractBnssStatistics(
            superGraph, \
            cross_time_graphs, \
            plotDir, bnssKey, \
            timeLength, \
            measuresToBeExtracted, logStats=False)
        serializeBnssStats(bnssKey, plotDir, statistics_for_bnss)


def intersection_between_users(usr_ids_for_bnss_in_time_window, bnssKey, superGraph):
    usrs_for_this_bnss = set([usrId for usrId, usr_type in superGraph.neighbors((bnssKey, SIAUtil.PRODUCT))])
    ins = usr_ids_for_bnss_in_time_window.intersection(usrs_for_this_bnss)
    if len(ins) > 10:
        print bnssKey, ins
    return len(ins)


def findUsersInThisTimeWindow(bnssKey, time_window, csvFolder, plotDir, timeLength = '1-W'):
     # Read data
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = readData(csvFolder)

    # Construct Graphs
    superGraph, cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict, \
                                                           bnssIdToBusinessDict, \
                                                           reviewIdToReviewsDict, timeLength)

    usr_ids_for_bnss_in_time_window = []

    lb, ub = time_window
    time_window = [idx for idx in range(lb, ub+1)]
    for time_key in time_window:
         time_g = cross_time_graphs[time_key]
         usr_ids_for_bnss_in_time_window = usr_ids_for_bnss_in_time_window \
                                           + [usrId for (usrId, usr_type)
                                              in time_g.neighbors((bnssKey, SIAUtil.PRODUCT))]
    usr_ids_for_bnss_in_time_window = set(usr_ids_for_bnss_in_time_window)
    bnssKeys = set([bnssId for usrId in usr_ids_for_bnss_in_time_window for bnssId, bnssType in superGraph.neighbors((usrId, SIAUtil.USER))])
    bnssKeys = [(bnssId, intersection_between_users(usr_ids_for_bnss_in_time_window, bnssId, superGraph)) for bnssId in bnssKeys]
    bnssKeys = sorted(bnssKeys, reverse=True,
                      key= lambda x: x[1])
    print bnssKeys


def logAllUsrStats(inputDir, timeLength = '1-W'):
    # Read data
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = readData(csvFolder)
    # Construct Graphs
    superGraph, cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict, \
                                                           bnssIdToBusinessDict, \
                                                           reviewIdToReviewsDict, timeLength)
    if not os.path.exists(plotDir):
        os.makedirs(plotDir)
    usrKeys = [usr_key for usr_key, usr_type in superGraph.nodes() \
                if usr_type == SIAUtil.USER]
    for usr_key in usrKeys:
        usrStatFilePath = os.path.join(plotDir, usr_key+'.stats')
        with open(usrStatFilePath, 'w') as usrStatFile:
            usrStatFile.write('--------------------------------------------------------------------------------------------------------------------\n')
            usrStatFile.write('Statistics for User:'+usr_key+'\n')
            neighboring_bnss_nodes = superGraph.neighbors((usr_key, SIAUtil.USER))
            reviews_for_usr = [superGraph.getReview(usr_key, bnssId) for (bnssId, bnss_type) in neighboring_bnss_nodes]
            usrStatFile.write('Reviews for this usr:')
            usrStatFile.write('Number of reviews:'+str(len(neighboring_bnss_nodes)))
            usrStatFile.write('\n')
            reviews_sorted = sorted(reviews_for_usr, key=lambda key: SIAUtil.getDateForReview(key))
            for review in reviews_sorted:
                usrStatFile.write(review.toString())
                usrStatFile.write('\n')


def logReviewsForUsrBnss(csvFolder, plotDir, timeLength='1-W'):
    # Read data
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = readData(csvFolder)
    # Construct Graphs
    superGraph, cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict, \
                                                           bnssIdToBusinessDict, \
                                                           reviewIdToReviewsDict, timeLength)
    if not os.path.exists(plotDir):
        os.makedirs(plotDir)
    for key in cross_time_graphs.keys():
        del cross_time_graphs[key]

    usr_to_no_of_reviews_dict = dict()
    bnss_to_no_of_reviews_dict = dict()

    usrKeys = [usr_key for usr_key, usr_type in superGraph.nodes() \
               if usr_type == SIAUtil.USER]

    for usrKey in usrKeys:
        no_of_reviews_for_usr = len(superGraph.neighbors((usrKey, SIAUtil.USER)))
        usr_to_no_of_reviews_dict[usrKey] = no_of_reviews_for_usr

    with open(os.path.join(plotDir, 'usr_review_cnt.txt'), 'w') as f:
        f.write(str(usr_to_no_of_reviews_dict))

    bnssKeys = [bnss_key for bnss_key, bnss_type in superGraph.nodes() \
               if bnss_type == SIAUtil.PRODUCT]


    for bnssKey in bnssKeys:
        no_of_reviews_for_bnss = len(superGraph.neighbors((bnssKey, SIAUtil.PRODUCT)))
        bnss_to_no_of_reviews_dict[bnssKey] = no_of_reviews_for_bnss

    with open(os.path.join(plotDir, 'bnss_review_cnt.txt'), 'w') as f:
        f.write(str(bnss_to_no_of_reviews_dict))