'''
Created on Feb 6, 2015

@author: santhosh
'''
import math
from datetime import datetime
from os.path import join

import dateutil
import pandas as pd

from util.SIAUtil import user, business, review

#appid,review id,userid,username,stars,version,date,number of helpful votes,total votes,unix timestamp
META_BNSS_ID = 'bnss_id'
META_REVIEW_ID = 'review_id'
META_USER_ID = 'user_id'
META_USER_NAME = 'username'
META_STARS = 'stars'
META_BNSS_VERSION = 'version'
META_DATE  = 'date'
META_HELPFUL_VOTES ='Helpful Votes'
META_TOTAL_VOTES = 'Total Votes'
META_TIMESTAMP = 'Timestamp'
META_COLS = [META_BNSS_ID,  META_REVIEW_ID, META_USER_ID, META_USER_NAME, \
             META_STARS, META_BNSS_VERSION, META_DATE, META_HELPFUL_VOTES, \
             META_TOTAL_VOTES, META_TIMESTAMP]

META_IDX_DICT = {META_COLS[i]:i for i in range(len(META_COLS))}

#appid,review id,title,content
BNSS_ID = 'bnss_id'
REVIEW_ID = 'review_id'
TITLE = 'title'
CONTENT = 'content'
COLS = [BNSS_ID, REVIEW_ID, TITLE, CONTENT]

REVW_IDX_DICT = {COLS[i]:i for i in range(len(COLS))}

META_FILE = 'swm_reviews_meta.csv'
REVIEW_FILE = 'swm_reviews_text.csv'

class SWMDataReader:
    def __init__(self):
        self.usrIdToUsrDict = {}
        self.bnssIdToBnssDict = {}
        self.reviewIdToReviewDict = {}

    def readData(self, reviewFolder, readReviewsText=False):
        beforeDataReadTime = datetime.now()
        reviewMetaFile = join(reviewFolder, META_FILE)
        reviewFile = join(reviewFolder, REVIEW_FILE)
        skippedMeta,skippedData = 0,0
        df1 = pd.read_csv(reviewMetaFile, escapechar='\\', header=None, dtype=object, error_bad_lines=False)
        for tup in df1.itertuples():
            ls = list(tup)
            if len(ls) < 11:
                skippedMeta += 1
            bnss_id, review_id, user_id, user_name, stars, version, review_date, hv, tv, ts = ls[1:11]
            # length = len(review_date)
            # review_date = review_date[0:length-4]+','+review_date[length-4:]
            #print bnss_id, review_id, user_id, user_name, stars, review_date
            #review_id = (bnss_id, review_id)
            try:
                date_object = dateutil.parser.parse(review_date)
                date_object = date_object.date()
                if date_object.year > 2012 or date_object.year < 2008:
                    raise Exception('Invalid Date')
                float_bnss_id = float(bnss_id)
                float_user_id = float(user_id)
                float_review_id = float(review_id)
                stars = float(stars)
                if math.isnan(stars) or stars < 0 or stars > 5:
                    #print 'Invalid Rating', stars
                    raise Exception('Invalid Rating')
            except:
                # print 'skipping Meta:', ls
                skippedMeta += 1
                continue

            if bnss_id not in self.bnssIdToBnssDict:
                self.bnssIdToBnssDict[bnss_id] = business(bnss_id, bnss_id)
            bnss = self.bnssIdToBnssDict[bnss_id]

            if user_id not in self.usrIdToUsrDict:
                self.usrIdToUsrDict[user_id] = user(user_id, user_name)
            usr = self.usrIdToUsrDict[user_id]

            revw = review(review_id, usr.getId(), bnss.getId(), stars, date_object)

            if review_id in self.reviewIdToReviewDict:
                print 'Already Read Meta - ReviewId:', review_id

            self.reviewIdToReviewDict[review_id] = revw

        print 'Users:', len(self.usrIdToUsrDict.keys()),\
            'Products:', len(self.bnssIdToBnssDict.keys()),\
            'Reviews:', len(self.reviewIdToReviewDict.keys())

        print 'Skipped Lines:', skippedMeta

        # return (self.usrIdToUsrDict, self.bnssIdToBnssDict, self.reviewIdToReviewDict)

        if not readReviewsText:
            return (self.usrIdToUsrDict, self.bnssIdToBnssDict, self.reviewIdToReviewDict)

        df2 = pd.read_csv(reviewFile,escapechar='\\', header=None,
                          dtype=object, error_bad_lines=False)
        review_ids = []
        for tup in df2.itertuples():
            try:
                index, bnss_id, review_id, title, content = tup
            except:
                skippedData += 1
                continue

            try:
                float_bnss_id = float(bnss_id)
                float_review_id = float(review_id)
            except:
                review_id = review_ids[-1]
                if review_id in self.reviewIdToReviewDict:
                    review_text = self.reviewIdToReviewDict[review_id].getReviewText()
                    review_text = review_text + bnss_id
                    self.reviewIdToReviewDict[review_id].setReviewText(review_text)
                continue

            review_ids.append(review_id)

            if review_id in self.reviewIdToReviewDict:
                review_text = str(content)
                self.reviewIdToReviewDict[review_id].setReviewText(review_text)
            else:
                skippedData += 1

        print 'Data lines', df2.shape[0], len(review_ids)

        afterDataReadTime = datetime.now()

        print 'Data Read Time:', (afterDataReadTime - beforeDataReadTime)
        print 'Skipped Count:', skippedMeta, skippedData

        print 'Users:', len(self.usrIdToUsrDict.keys()),\
            'Products:', len(self.bnssIdToBnssDict.keys()),\
            'Reviews:', len(self.reviewIdToReviewDict.keys())

        # textLessReviewIds = set([review_id for review_id in self.reviewIdToReviewDict
        #                         if not self.reviewIdToReviewDict[review_id].getReviewText()])
        # for review_id in textLessReviewIds:
        #     del self.reviewIdToReviewDict[review_id]
        #
        # print 'Removing text less reviews'
        #
        # print 'Users:', len(self.usrIdToUsrDict.keys()),\
        #     'Products:', len(self.bnssIdToBnssDict.keys()),\
        #     'Reviews:', len(self.reviewIdToReviewDict.keys())

        return (self.usrIdToUsrDict, self.bnssIdToBnssDict, self.reviewIdToReviewDict)


#     def readDataWithPandas(self, reviewFolder):
#         reviewMetaFile = join(reviewFolder, META_FILE)
#
#         df1 = pd.read_csv(reviewMetaFile,escapechar='\\',header=None,\
#                               dtype=object)
#
#         df1 =  df1.dropna(axis=0, how='all')
#
#         reviewFile = join(reviewFolder, REVIEW_FILE)
#
#         df2 = pd.read_csv(reviewFile,escapechar='\\',header=None,\
#                               dtype=object, names = COLS)
#
#         df2 = df2.dropna(axis=0, how='all')
#         print df1.describe()
#
#         for index,row in df1.iterrows():
#             print index
#             print row
#             break
#
#         for row in df1.itertuples():
#             print row
#             break
#
#         sys.exit()
#
#         for row in df1.itertuples():
#             print row
#             row = row[0]
#             bnss_id = row[META_IDX_DICT[META_BNSS_ID]]
#             user_id = row[META_IDX_DICT[META_USER_ID]]
#             user_name = row[META_IDX_DICT[META_USER_NAME]]
#             review_id = row[META_IDX_DICT[META_REVIEW_ID]]
#             stars = row[META_IDX_DICT[META_STARS]]
#             review_date = row[META_IDX_DICT[META_DATE]]
#
#             review_id = (bnss_id, review_id)
#
#             try :
#                 date_object = dateutil.parser.parse(review_date)
#                 date_object = date_object.date()
#             except:
#                 e = sys.exc_info()[0]
#                 print e
#                 continue
#             try:
#                 stars = float(stars)
#             except:
#                 e = sys.exc_info()[0]
#                 print e
#                 continue
#
#             if bnss_id not in self.bnssIdToBnssDict:
#                 self.bnssIdToBnssDict[bnss_id] = business(bnss_id, bnss_id)
#             bnss = self.bnssIdToBnssDict[bnss_id]
#
#             if user_id not in self.usrIdToUsrDict:
#                 self.usrIdToUsrDict[user_id] = user(user_id, user_name)
#             usr = self.usrIdToUsrDict[user_id]
#
#
#             revw = review(review_id, usr.getId(), bnss.getId(), stars, date_object)
#
#             if review_id in self.reviewIdToReviewDict:
#                 print 'already there',review_id
#
#             self.reviewIdToReviewDict[review_id] = revw
#
#         with open(reviewFile,mode= 'rU') as f:
#             lines = csv.reader(f, escapechar='\\')
#             for row in lines:
#                 break
#                 line = line.replace('\,','')
#                 row = line.split(',')
#                 if len(row) < len(COLS):
#                     print 'skipping Data:', line, row
#                     skippedData+=1
#                     continue
#                 bnss_id = row[0]
#                 review_id = row[1]
#                 review_id = (bnss_id, review_id)
#                 review_text = row[3]
#                 if review_id not in self.reviewIdToReviewDict:
#                     print 'Not Read Meta Data - ReviewId:', review_id
#                     skippedData+=1
#                     continue
#                 self.reviewIdToReviewDict[review_id].setReviewText(review_text)
#
#         for row2 in df2.itertuples():
#             bnss_id = row2[1]
#             review_id = row2[2]
#             review_id = (bnss_id, review_id)
#             review_text = row2[4]
#             if review_id not in self.reviewIdToReviewDict:
#                 #print 'Not Present', review_id
#                 continue
#
#             self.reviewIdToReviewDict[review_id].setReviewText(review_text)
#
#
#         return (self.usrIdToUsrDict, self.bnssIdToBnssDict, self.reviewIdToReviewDict)
