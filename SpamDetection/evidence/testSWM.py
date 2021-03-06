'''
Created on Jan 6, 2016

@author: santhosh
'''

from main import AppUtil
from datetime import datetime
import sys, os
import CommonUtil

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"evidence.testSWM\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]

    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'it')

    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    bnss_key_time_wdw_list = [('284819997', (166, 171)), ('284819997', (173, 178)),
                            ('284819997', (180, 185)), ('284819997', (187, 192)),
                            ('319927587', (189, 194)), ('284235722', (147,152))]
    # Rating Distribution
    bnss_key_time_wdw_list = [('284819997', (168, 169)), ('284819997', (175, 176)),
                            ('284819997', (182, 183)), ('284819997', (189, 190)),
                            ('319927587', (191, 192)), ('284235722', (149,150))]
    # Time wise Rating
    bnss_key_time_wdw_list = [('284819997', (167, 170)), ('284819997', (174, 177)),
                            ('284819997', (181, 184)), ('284819997', (188, 191)),
                            ('319927587', (190, 193)), ('284235722', (148,151))]
    # Word Clouds
    bnss_key_time_wdw_list = [('284819997', (75, 166)), ('284819997', (168, 169)),
                              ('284819997', (175, 176)), ('284819997', (182, 183)),
                              ('284819997', (189, 190)), ('319927587', (191, 192))]
    bnss_key_time_wdw_list = [('284819997', (189, 190))]

#     bnss_key_time_wdw_list = [('284819997', (167, 169))]
    CommonUtil.doGatherEvidence(csvFolder, plotDir, bnss_key_time_wdw_list=bnss_key_time_wdw_list)

