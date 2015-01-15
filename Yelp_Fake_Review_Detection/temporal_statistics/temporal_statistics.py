'''
Created on Dec 29, 2014

@author: santhosh
'''
from datetime import datetime, timedelta
import math
import numpy
import os
from os.path import join
import random
import sys
from util import PlotUtil
from util import SIAUtil
from util import StatConstants
from util.GraphUtil import SuperGraph, TemporalGraph
from util.ScrappedDataReader import ScrappedDataReader
from intervaltree import Interval,IntervalTree


def sigmoid_prime(x):
    return (2.0/(1+math.exp(-x)))-1

def entropyFn(probability_dict):
    entropy = 0
    for key in probability_dict:
        probability = probability_dict[key]
        if probability > 0:
            entropy += -(probability*math.log(probability,2))
    return entropy

def constructIntervalTree(days):
    t = IntervalTree()
    end = days
    t[0:1] = 0
    iter_start = 1
    step_index = 0
    while(iter_start<end):
        iterend = iter_start+(2**step_index)
        t[iter_start:iterend] = 0
        iter_start =  iterend
        step_index+=1
    return t


def getBucketIntervalForBucketTree(bucketTree, point):
    bucket_intervals = list(bucketTree[point])
    assert len(bucket_intervals) == 1
    return bucket_intervals[0]

def updateBucketTree(bucketTree, point):
    interval = getBucketIntervalForBucketTree(bucketTree, point)
    begin,end,data = interval
    bucketTree.remove(interval)
    bucketTree[begin:end] = data + 1.0
    
def generateStatistics(superGraph, cross_time_graphs, usrIdToUserDict, bnssIdToBusinessDict, reviewIdToReviewsDict):
    bnss_statistics = dict()
    total_time_slots = len(cross_time_graphs.keys())
    
    for timeKey in cross_time_graphs.iterkeys():
        G = cross_time_graphs[timeKey]
        for bnssId in G.getBusinessIds():
            if bnssId not in bnss_statistics:
                bnss_statistics[bnssId] = dict()
                bnss_statistics[bnssId][StatConstants.FIRST_TIME_KEY] = timeKey
            bnss_name = bnssIdToBusinessDict[bnssId].getName()
            #Average Rating
            if StatConstants.AVERAGE_RATING not in bnss_statistics[bnssId]:
                bnss_statistics[bnssId][StatConstants.AVERAGE_RATING] = numpy.zeros(total_time_slots)
                
            neighboring_usr_nodes = G.neighbors((bnssId,SIAUtil.PRODUCT))
            reviews_for_bnss = []
            for (usrId, usr_type) in neighboring_usr_nodes:
                review_for_bnss = G.getReview(usrId,bnssId)
                reviews_for_bnss.append(review_for_bnss)
            ratings = [review.getRating() for review in reviews_for_bnss]
            bnss_statistics[bnssId][StatConstants.AVERAGE_RATING][timeKey] = float(sum(ratings))
            
            #Rating Entropy
            sorted_rating_list = set(sorted(ratings))
            if StatConstants.RATING_DISTRIBUTION not in bnss_statistics[bnssId]:
                bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION] = dict()
                
            if timeKey not in bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION]:
                bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION][timeKey] = {key:0.0 for key in sorted_rating_list}
            
            for rating in ratings:
                bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION][timeKey][rating] += 1.0
            
            for rating in sorted_rating_list:
                bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION][timeKey][rating] /= float(len(reviews_for_bnss)) 
            
            
            #NumberOfReviews
            if StatConstants.NO_OF_REVIEWS not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][StatConstants.NO_OF_REVIEWS] = numpy.zeros(total_time_slots)
            noOfReviews = len(neighboring_usr_nodes)
            bnss_statistics[bnssId][StatConstants.NO_OF_REVIEWS][timeKey] = noOfReviews
            
            #Ratio of Singletons
            if StatConstants.RATIO_OF_SINGLETONS not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][StatConstants.RATIO_OF_SINGLETONS] = numpy.zeros(total_time_slots)
            noOfSingleTons = 0
            for neighbor in neighboring_usr_nodes:
                if len(superGraph.neighbors(neighbor)) == 1:
                    noOfSingleTons+=1
            bnss_statistics[bnssId][StatConstants.RATIO_OF_SINGLETONS][timeKey] = float(noOfSingleTons)/float(len(reviews_for_bnss))        
            
            #Ratio of First Timers
            if StatConstants.RATIO_OF_FIRST_TIMERS not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][StatConstants.RATIO_OF_FIRST_TIMERS] = numpy.zeros(total_time_slots)
            noOfFirstTimers = 0
            for usr_neighbor in neighboring_usr_nodes:
                (usrId, usr_type) = usr_neighbor
                current_temporal_review = G.getReview(usrId, bnssId)
                allReviews = [superGraph.getReview(usrId, super_graph_bnssId) \
                              for (super_graph_bnssId, super_graph_bnss_type) in superGraph.neighbors(usr_neighbor)]
                firstReview = min(allReviews, key= lambda x: SIAUtil.getDateForReview(x))
                if firstReview.getId() == current_temporal_review.getId():
                    noOfFirstTimers+=1
            bnss_statistics[bnssId][StatConstants.RATIO_OF_FIRST_TIMERS][timeKey] = float(noOfFirstTimers)/float(len(reviews_for_bnss))
            
            #Youth Score
            if StatConstants.YOUTH_SCORE not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][StatConstants.YOUTH_SCORE] = numpy.zeros(total_time_slots)
            youth_scores = []
            for usr_neighbor in neighboring_usr_nodes:
                (usrId, usr_type) = usr_neighbor
                allReviews = [superGraph.getReview(usrId, super_graph_bnssId) \
                              for (super_graph_bnssId, super_graph_bnss_type) in superGraph.neighbors(usr_neighbor)]
                allReviews = sorted(allReviews, key= lambda x: SIAUtil.getDateForReview(x))
                current_temporal_review = G.getReview(usrId, bnssId)
                reviewAge = (SIAUtil.getDateForReview(current_temporal_review)-SIAUtil.getDateForReview(allReviews[0])).days
                youth_score = 1-sigmoid_prime(reviewAge)
                youth_scores.append(youth_score)
            bnss_statistics[bnssId][StatConstants.YOUTH_SCORE][timeKey] = numpy.mean(numpy.array(youth_scores))
            
            #Entropy Score
            entropyScore= 0
            
            if StatConstants.ENTROPY_SCORE not in bnss_statistics[bnssId]:
                bnss_statistics[bnssId][StatConstants.ENTROPY_SCORE] = numpy.zeros(total_time_slots)
                
            if noOfReviews >= 2:
                bucketTree = constructIntervalTree(60)
                allReviewsInThisTimeBlock = [G.getReview(usrId, bnssId) for (usrId, usr_type) in neighboring_usr_nodes]
                allReviewsInThisTimeBlock = sorted(allReviewsInThisTimeBlock, key = lambda x: SIAUtil.getDateForReview(x))
                allReviewVelocity = [ (SIAUtil.getDateForReview(allReviewsInThisTimeBlock[x+1]) - \
                                       SIAUtil.getDateForReview(allReviewsInThisTimeBlock[x])).days \
                                     for x in range(len(allReviewsInThisTimeBlock)-1)]
                for reviewTimeDiff in allReviewVelocity:
                    updateBucketTree(bucketTree, reviewTimeDiff)
                
                if StatConstants.REVIEW_TIME_VELOCITY not in bnss_statistics[bnssId]:
                    bnss_statistics[bnssId][StatConstants.REVIEW_TIME_VELOCITY] = dict()
                    
                bnss_statistics[bnssId][StatConstants.REVIEW_TIME_VELOCITY][timeKey] = allReviewVelocity
                 
                rating_velocity_prob_dist = {(begin,end):(count_data/(noOfReviews-1)) for (begin, end, count_data) in bucketTree}
                
                entropyScore = entropyFn(rating_velocity_prob_dist)
                bnss_statistics[bnssId][StatConstants.ENTROPY_SCORE][timeKey] = entropyScore
#                 print bnss_name, noOfReviews, range(len(allReviewsInThisTimeBlock)-1)
#                 print [SIAUtil.getDateForReview(r) for r in allReviewsInThisTimeBlock]
#                 print reviewVelocityVector, rating_velocity_prob_dist
            
            
            #Max Text Similarity
    
    
    #POST PROCESSING FOR REVIEW AVERAGE_RATING, NO_OF_REVIEWS, RATING_ENTROPY and ENTROPY_SCORE
    for bnss_key in bnss_statistics:
        statistics_for_bnss = bnss_statistics[bnss_key]
        no_of_reviews_for_bnss = statistics_for_bnss[StatConstants.NO_OF_REVIEWS]
            
#         for timeKey in range(total_time_slots):
#             rating_sum_for_bnss[timeKey] = no_of_reviews_for_bnss[timeKey]*avg_rating_for_bnss[timeKey]
#             
#         if bnssIdToBusinessDict[bnss_key].getName() == 'Arizona Humane Society':
#             print statistics_for_bnss[NO_OF_REVIEWS],statistics_for_bnss[AVERAGE_RATING]
            
        for timeKey in range(total_time_slots):
            if timeKey > 0:
                #POST PROCESSING FOR NUMBER_OF_REVIEWS
                statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey] = no_of_reviews_for_bnss[timeKey-1]+no_of_reviews_for_bnss[timeKey]
                #POST PROCESSING FOR AVERAGE RATING
                if no_of_reviews_for_bnss[timeKey] > 0:
                    sum_of_ratings = (statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey-1]*no_of_reviews_for_bnss[timeKey-1])
                    sum_of_ratings += statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey]
                    statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] = sum_of_ratings/no_of_reviews_for_bnss[timeKey]
                else:
                    statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] = 0
            else:
                if no_of_reviews_for_bnss[timeKey] > 0:
                    statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] /=  statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey]
            
            #POST PROCESSING FOR RATING ENTROPY
            if timeKey in statistics_for_bnss[StatConstants.RATING_DISTRIBUTION]:
                entropy = entropyFn(statistics_for_bnss[StatConstants.RATING_DISTRIBUTION][timeKey])
                if StatConstants.RATING_ENTROPY not in statistics_for_bnss:
                    statistics_for_bnss[StatConstants.RATING_ENTROPY] = numpy.zeros(total_time_slots)
                statistics_for_bnss[StatConstants.RATING_ENTROPY][timeKey] = entropy
                
#         if bnssIdToBusinessDict[bnss_key].getName() == 'Matsuhisa':               
#         if bnssIdToBusinessDict[bnss_key].getName() == 'Arizona Humane Society':
#             print statistics_for_bnss[NO_OF_REVIEWS],statistics_for_bnss[AVERAGE_RATING]
            
    return bnss_statistics



        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python temporal_statistics.py fileName'
        sys.exit()
    inputFileName = sys.argv[1]
    
    beforeGraphPopulationTime = datetime.now()
    #(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = dataReader.parseAndCreateObjects(inputFileName)
    
    rdr = ScrappedDataReader()
    
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = rdr.readData(inputFileName)
    superGraph = SuperGraph.createGraph(usrIdToUserDict,\
                                             bnssIdToBusinessDict,\
                                             reviewIdToReviewsDict)
    
    cross_time_graphs = TemporalGraph.createTemporalGraph(usrIdToUserDict,\
                                             bnssIdToBusinessDict,\
                                             reviewIdToReviewsDict,\
                                             '2-M', False)
    bnss_statistics = generateStatistics(superGraph, cross_time_graphs, usrIdToUserDict, bnssIdToBusinessDict, reviewIdToReviewsDict)
    
    #sys.exit()
    
    bnssKeys = [bnss_key for bnss_key in bnss_statistics]
    
    bnssKeys = sorted(bnssKeys, reverse=True, key = lambda x: len(superGraph.neighbors((x,SIAUtil.PRODUCT))))
    
    colors = ['g', 'c', 'r', 'b', 'm', 'y', 'k']
    
    inputDir =  join(join(join(inputFileName, os.pardir),os.pardir), 'latest')
    i=0
    while i<100:
        PlotUtil.plotBnssStatistics(bnss_statistics, bnssIdToBusinessDict, bnssKeys[i], len(cross_time_graphs.keys()), inputDir, random.choice(colors))
        i+=1