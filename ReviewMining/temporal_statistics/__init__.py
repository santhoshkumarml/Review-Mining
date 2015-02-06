"""
Simple demo with multiple subplots.


"""
import numpy as np
import matplotlib.pyplot as plt
from lshash import LSHash
from util import SIAUtil
import networkx
from os.path import join
import json
from yelp_utils import YelpDataReader.ScrappedDataReader
from yelp_utils import dataReader as dr
from temporal_statistics import measure_extractor
from util.GraphUtil import SuperGraph
import sys

def checkPlot():
    x1 = [0, 1, 2, 3, 4]
    y1 = [1, 1, 1, 1, 1]
    #plt.figure(figsize=(16, 18))
    plt.title('A tale of 2 subplots')
    plt.ylabel('Damped oscillation')
    plt.ylim(1,max(y1)+1)
    plt.plot(x1, y1)
#     for i in range(1, 10):
#         ax = plt.subplot(len(range(1, 10)), 1, i)
#         #plt.ylim((1,5))
#         plt.yticks(range(1, 6))
#         ax.grid('off')
#         ax.plot(x1, y1, 'yo-')
#         plt.title('A tale of 2 subplots')
#         plt.ylabel('Damped oscillation' + str(i))
#     plt.tight_layout()
    plt.show()    

def checklshash():
    lsh = LSHash(6, 8)
    lsh.index([1,2,3,4,5,6,7,8])
    lsh.index([2,3,4,5,6,7,8,9])
    lsh.index([10,12,99,1,5,31,2,3])
    print lsh.query([1,2,3,4,5,6,7,7])


def checkRestaurant():
    inputFileName = '/media/santhosh/Data/workspace/datalab/data/master.data'  
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = dr.parseAndCreateObjects(inputFileName)
    #G = SuperGraph.createGraph(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict)
    for bnssKey in bnssIdToBusinessDict:
        if bnssIdToBusinessDict[bnssKey].getName()=='Cheese Board Pizza':
            print bnssIdToBusinessDict[bnssKey].getUrl()


    
def checkNewReader():
    #inputDirName = 'D:\\workspace\\datalab\\data\\NYC'
    #inputDirName = 'D:\\workspace\\datalab\\NYCYelpData2'
    #inputDirName = '/media/santhosh/Data/workspace/datalab/NYCYelpData2'
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/from ubuntu/zips'
    #\\2 Duck Goose.txt
    #\\Cafe Habana.txt
    rdr = YelpDataReader()
    rdr.readData(inputDirName)    
    G = SuperGraph.createGraph(rdr.getUsrIdToUsrDict(), rdr.getBnssIdToBnssDict(), rdr.getReviewIdToReviewDict())
    
    cc = sorted(networkx.connected_component_subgraphs(G, False), key=len, reverse=True)
    
    for g in cc:
        cbnssNodes = [node for node in g.nodes() if node[1] == SIAUtil.PRODUCT]
        for node in cbnssNodes:
            bnss = rdr.getBnssIdToBnssDict()[node[0]]
            print bnss.getId(), len(g.neighbors(node))
        print '-----------------------------------'
    
    bnssNodes = [node for node in G.nodes() if node[1] == SIAUtil.PRODUCT]
    bnssNodes = sorted(bnssNodes, reverse=True, key = lambda x: len(G.neighbors(x)))
    usrNodes = [node for node in G.nodes() if node[1] == SIAUtil.USER]
    usrNodes = sorted(usrNodes, reverse=True, key = lambda x: len(G.neighbors(x)))
    print len(bnssNodes), len(usrNodes)
    
    for bnssNode in bnssNodes:
        bnss = rdr.getBnssIdToBnssDict()[bnssNode[0]]
        print bnss.getName(), len(G.neighbors(bnssNode))
    
    print '=============================================================================='
    
    for usrNode in usrNodes:
        usr = rdr.getUsrIdToUsrDict()[usrNode[0]]
        print usr.getName(), usr.getUsrExtra(), len(G.neighbors(usrNode))
        
#     for bnssKey in rdr.getBnssIdToBnssDict():
#         if 'Halal Guys' in rdr.getBnssIdToBnssDict()[bnssKey].getName():
#             print rdr.getBnssIdToBnssDict()[bnssKey].getName(), len(G.neighbors((bnssKey,SIAUtil.PRODUCT)))
#     usrKeys = [usrKey for usrKey in rdr.getUsrIdToUsrDict()]
#     usrKeys = sorted(usrKeys, reverse=True, key = lambda x: len(G.neighbors((x,SIAUtil.USER))))
#     
#     for usrKey in usrKeys:
#         neighbors = G.neighbors((usrKey,SIAUtil.USER))
#         if len(neighbors) > 2 and len(neighbors)<10:
#             allReviews = [G.getReview(usrKey, neighbor[0]) for neighbor in neighbors]
#             rec_reviews = [r for r in allReviews if r.isRecommended()]
#             not_rec_reviews = [r for r in allReviews if not r.isRecommended()]
#             if len(rec_reviews)>0 and len(not_rec_reviews)>0:
#                 usr = rdr.getUsrIdToUsrDict()[usrKey]
#                 print usr.getName(),usr.getUsrExtra(), len(neighbors)
#                 for r in rec_reviews:
#                     print 'Rec', r.getBusinessID(), r.getTimeOfReview()
#                 for r in not_rec_reviews:
#                     print 'Not Rec', r.getBusinessID(), r.getTimeOfReview()
     
    
def doIndexForRestaurants():
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/from ubuntu/zips'
    rdr = YelpDataReader()
    rdr.readData(inputDirName)
    result = dict()
    restaurants = []
    for bnssKey in rdr.getBnssIdToBnssDict():
        addr = bnssKey[1]
        bnss = rdr.getBnssIdToBnssDict()[bnssKey]
        outDict = dict()
        outDict['address'] = addr
        outDict['bnssName'] = bnss.getName()
        restaurants.append(outDict)
    result['bnss'] = restaurants
    with open(join(inputDirName, 'index.json'),'w') as f:
        json.dump(result, f)
         
        
def checkBucketTree():
    bucketTree = measure_extractor.constructIntervalTree(60)
    print bucketTree
    inputData = [1,4,4,4,8,16,32]
    for i in inputData:
        interval = measure_extractor.getBucketIntervalForBucketTree(bucketTree, i)
        begin,end,data = interval
        bucketTree.remove(interval)
        bucketTree[begin:end] = data+1.0
        
    print bucketTree
    
    rating_velocity_prob_dist = {(begin,end):(count_data/(6)) for (begin, end, count_data) in bucketTree}
    
    print rating_velocity_prob_dist
    
def checkYelpAPI():
    inputDirName = '/home/santhosh'
    rdr = YelpDataReader()
    rdr.readDataForBnss(inputDirName, 'Boho Cafe.txt')
    revws1 = rdr.getReviewIdToReviewDict().values()
    content = 'data='
    revws2 = []
    with open(join(inputDirName, 'bnss'), mode='r') as f:
        data = dict()
        content = content+f.readline()
        exec(content)
        revws2 = data['reviews']
    print len(revws1),len(revws2)

def checkUsersWithOnlyNotRecommendedReviews():
#     inputDirName = 'D:\\workspace\\datalab\\data\\z'
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/z'
    rdr = YelpDataReader()
    rdr.readData(inputDirName)
    print 'Read Data'
    G = SuperGraph.createGraph(rdr.getUsrIdToUsrDict(), rdr.getBnssIdToBnssDict(), rdr.getReviewIdToReviewDict())
    print 'Graph Constructed'
    allUserIds = set([usrid for (usrid,usrtype) in G.nodes() if usrtype == SIAUtil.USER])
    usersWithAleastOneRecReviews = set()
    usersWithOnlyOneReview = set()
    for usrId in allUserIds:
        usr = rdr.getUsrIdToUsrDict()[usrId]
        usrExtra = usr.getUsrExtra()
        reviewCountString = usrExtra[1]
        reviewCountSplit = reviewCountString.split()
        reviewCount = int(reviewCountSplit[0])
        if reviewCount == 1:
            usersWithOnlyOneReview.add(usrId)

        bnss_nodes = G.neighbors((usrId,SIAUtil.USER))
        allReviews = [G.getReview(usrId, bnssId) for bnssId,bnssType in bnss_nodes]
        hasOneRecommended = False
        for revw in allReviews:
            if revw.isRecommended():
                hasOneRecommended = True
                break
        if hasOneRecommended:
            usersWithAleastOneRecReviews.add(usrId)
    
    usersWithNotRecommendedReviewsAlone = allUserIds-usersWithAleastOneRecReviews
    usersWithMultipleReviewsAndNotRecommendedReviewsAlone =\
     usersWithNotRecommendedReviewsAlone-usersWithOnlyOneReview
     
    print 'Total Users',len(allUserIds)
    print 'usersWithOnlyOneReview', len(usersWithOnlyOneReview)
    print 'usersWithAlteastOneRecReviews', len(usersWithAleastOneRecReviews)
    print 'usersWithNotRecommendedReviewsAlone', len(usersWithNotRecommendedReviewsAlone)  
    print 'usersWithMultipleNotRecReviewsAlone',len(usersWithMultipleReviewsAndNotRecommendedReviewsAlone)
        
def checkBnss():
#     inputDirName = 'D:\\workspace\\datalab\\data\\z'
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/r'
    rdr = YelpDataReader()
    rdr.readData(inputDirName)
    print len(rdr.getBnssIdToBnssDict())

def plotDirCreation(inputFileName):
    import os
    inputDir =  join(join(join(inputFileName, os.pardir),os.pardir), 'latest')