# time_predictor

# race time predictor using various methods
#  1a) purdy points: standard calculation
#  1b) purdy points: least squares model
#   2) vo2max
#   3) cameron method
#   4) riegel method

import math
from datetime import datetime as date

def time_convert(time):
    # convert time in seconds to string time hh:mm:ss
    hours = int(time // 3600)
    minutes = int(time % 3600 // 60)
    seconds = int(time % 3600 % 60)

    time_format = date(1, 1, 1, hours, minutes, seconds)
    time_format = date.strftime(time_format, '%H:%M:%S')
    return time_format

###############################################
## purdy points method: standard calculation ##
###############################################

# purdy, j. g. 'computer generated track scoring tables, medicine and science in sports', vol. 2, no. 3, 152-161, fall 1970

# pull values from performance table
def velocity_table(distance):

    # table of world records per 1936 = 950 purdy points
    perform_table = [40, 11.000,
                     50, 10.9960,
                     60, 10.9830,
                     70, 10.9620,
                     80, 10.934,
                     90, 10.9000,
                     100, 10.8600,
                     110, 10.8150,
                     120, 10.765,
                     130, 10.7110,
                     140, 10.6540,
                     150, 10.5940,
                     160, 10.531,
                     170, 10.4650,
                     180, 10.3960,
                     200, 10.2500,
                     220, 10.096,
                     240, 9.9350,
                     260, 9.7710,
                     280, 9.6100,
                     300, 9.455,
                     320, 9.3070,
                     340, 9.1660,
                     360, 9.0320,
                     380, 8.905,
                     400, 8.7850,
                     450, 8.5130,
                     500, 8.2790,
                     550, 8.083,
                     600, 7.9210,
                     700, 7.6690,
                     800, 7.4960,
                     900, 7.32000,
                     1000, 7.18933,
                     1200, 6.98066,
                     1500, 6.75319,
                     2000, 6.50015,
                     2500, 6.33424,
                     3000, 6.21913,
                     3500, 6.13510,
                     4000, 6.07040,
                     4500, 6.01822,
                     5000, 5.97432,
                     6000, 5.90181,
                     7000, 5.84156,
                     8000, 5.78889,
                     9000, 5.74211,
                     10000, 5.70050,
                     12000, 5.62944,
                     15000, 5.54300,
                     20000, 5.43785,
                     25000, 5.35842,
                     30000, 5.29298,
                     35000, 5.23538,
                     40000, 5.18263,
                     50000, 5.08615,
                     60000, 4.99762,
                     80000, 4.83617,
                     100000, 4.68988]

    for i in range(0, 116, 2):
        if distance < perform_table[i]:
            if i == 0:
                index = 0
            else:
                index = i - 2
            break
    
    dist_floor = perform_table[index]
    time_floor = dist_floor / perform_table[index + 1]
    dist_below = perform_table[index - 2]
    time_below = dist_below / perform_table[index - 1]
    vel_time = time_below + (time_floor - time_below) * (distance - dist_below) / (dist_floor - dist_below)
    velocity = distance / vel_time
    return velocity, vel_time
    
# calculate slowdown time from curves (implies track races)
def frac(distance):
    if distance < 110:
        slowdown = 0
    else:
        laps_whole = distance // 400 # integer laps
        laps_part_m = distance % 400   # partial laps in meters
        if laps_part_m <= 50:
            laps_part = 0
        elif laps_part_m <= 150:
            laps_part = laps_part_m - 50
        elif laps_part_m <= 250:
            laps_part = 100
        elif laps_part_m <= 350:
            laps_part = laps_part_m - 150
        elif laps_part_m < 400:
            laps_part = 200
        time_slow = 200 * laps_whole + laps_part # slowdown time in seconds
        slowdown = time_slow / distance
    return slowdown

def purdy_standard(time_perform, dist_perform, dist_predict):
    # find performance distance and velocities
    velocity, vel_time = velocity_table(dist_perform)

    # add startup and curve slowdown times
    slowdown = frac(dist_perform)
    time_950 = vel_time + 0.28 * velocity + 0.0065 * slowdown * velocity ** 2

    k = 0.0654 - 0.00258 * velocity
    a = 85 / k
    b = 1 - 950 / a

    # calculate purdy points
    purdy_points = a * (time_950 / time_perform - b)
    
    # find desired distance and velocities
    velocity, vel_time = velocity_table(dist_predict)

    # add startup and curve slowdown times
    slowdown = frac(dist_perform)
    time_950 = vel_time + 0.28 * velocity + 0.0065 * slowdown * velocity ** 2
    
    k = 0.0654 - 0.00258 * velocity
    a = 85 / k
    b = 1 - 950 / a
    
    # calculate time corresponding to purdy point value
    time_purdy_standard = time_950 / (purdy_points / a + b)
    return time_purdy_standard

##############################################
## purdy points method: least squares model ##
##############################################
    
# purdy, j. g. 'least squares model of the running curve', research quaterly", 45:224-238, october 1974

# create running curve equation
def curve(distance):
    b1 = 11.15895
    b2 = 4.304605
    b3 = 0.5234627
    b4 = 4.031560
    b5 = 2.316157

    r1 = 3.796158e-2
    r2 = 1.646772e-3
    r3 = 4.107670e-4
    r4 = 7.068099e-6
    r5 = 5.220990e-9

    velocity = -b1 * math.exp(-r1 * distance)
    velocity += b2 * math.exp(-r2 * distance)
    velocity += b3 * math.exp(-r3 * distance)
    velocity += b4 * math.exp(-r4 * distance)
    velocity += b5 * math.exp(-r5 * distance)
    
    vel_time = distance / velocity
    return velocity, vel_time

def purdy_leastsq(time_perform, dist_perform, dist_predict):
    velocity, vel_time = curve(dist_perform)

    k = 0.0654 - 0.00258 * velocity
    a = 85 / k
    b = 1 - 1035 / a
    purdy_points = a * (vel_time / time_perform - b)

    velocity, vel_time = curve(dist_predict)

    k = 0.0654 - 0.00258 * velocity
    a = 85 / k
    b = 1 - 1035 / a
    time_purdy_leastsq = vel_time / (purdy_points / a + b)
    return time_purdy_leastsq


###################
## vo2max method ##
###################

# resources from mcmillanrunning.com

def vo2max(time_perform, dist_perform, dist_predict, time_start):
    # calculate vo2max from previous time
    v = dist_perform / time_perform
    vo2 = -4.60 + 0.182258 * v + 0.000104 * v ** 2
    permax = 0.8 + 0.1894393 * math.exp(-0.012778 * time_perform)
    permax += 0.2989558 * math.exp(-0.1932605 * time_perform)
    vo2max = vo2 / permax
    
    # use previous predicted time (purdy standard) as starting value for predicted vo2max time 
    time_test = time_start / 60
    v_test = dist_predict / time_start
    vo2_test = -4.60 + 0.182258 * v_test + 0.000104 * v_test ** 2
    permax_test = 0.8 + 0.1894393 * math.exp(-0.012778 * time_test) + 0.2989558 * math.exp(-0.1932605 * time_test)
    vo2max_test = vo2_test / permax_test
    
    # check percent difference for minimum accuracy
    while abs((vo2max_test - vo2max) / vo2max) > 0.001:
        # adjust goal time
        if (vo2max_test - vo2max) / vo2max > 0:
            time_test += 0.001
        if (vo2max_test - vo2max) / vo2max < 0:
            time_test -= 0.001

        # recalculate parameters
        v_test = dist_predict / time_test
        vo2_test = -4.60 + 0.182258 * v_test + 0.000104 * v_test ** 2
        permax_test = 0.8 + 0.1894393 * math.exp(-0.012778 * time_test) + 0.2989558 * math.exp(-0.1932605 * time_test)
        vo2max_test = vo2_test / permax_test

    time_vo2max = 60 * time_test
    return time_vo2max


############################
## david f. cameron model ##
############################

# resources from mcmillanrunning.com
def cameron(time_perform, dist_perform, dist_predict):
    # list of valid distances
    valid_table = [400, 600, 800, 1000, 1500, 1609.344, 2000, 3000, 3218.688,
    4828.032, 5000, 6437.376, 8046.72, 10000, 12070.08, 15000, 16093.44, 21097.5, 42195, 80467.2]


    dist_perf_check = dist_perform * 1609.344
    dist_pred_check = dist_predict * 1609.344
    perform_offset = abs(dist_perf_check - valid_table[0])
    predict_offset = abs(dist_pred_check - valid_table[0])

    for i in range(1, 20):
        perform_check = abs(dist_perf_check - valid_table[i])
        predict_check = abs(dist_pred_check - valid_table[i])
        
        if perform_check >= perform_offset and predict_check >= predict_offset:
            break
        if perform_check < perform_offset:
            perform_offset = perform_check
        if predict_check < predict_offset:
            predict_offset = predict_check
        

    fac = time_perform / (3600 / (13.49681 - (0.048865 * dist_predict) + (2.438936 / (dist_perform ** 0.7905)))) / dist_perform
    time_cameron = fac * (3600 / (13.49681 - (0.048865 * dist_predict) + (2.438936 / (dist_predict ** 0.7905)))) * dist_predict
    return time_cameron, perform_offset, predict_offset


#######################
## pete riegel model ##
#######################

# 'time predicting', runner's world, august 1977
# refined: 'athletic records and human Endurance', american scientists, may-june 1981

def riegel(time_perform, dist_perform, dist_predict):
    time_reigel = time_perform * (dist_predict / dist_perform) ** 1.06
    return time_reigel


################################
###### main + user prompts #####
################################
    
def time_predictor():
    # input parameters and error messages
    dist_perform = input('performance distance (meters, if in miles end with m): ')
    while dist_perform == '': # wait for input
        print('\nerror: missing distance')
        dist_perform = input('performance distance (meters, if in miles end with m): ')

    time_perform = input('performance time (h:m:s): ')
    while time_perform == '': # wait for input
        print('\nerror: missing time')
        time_perform = input('performance time (h:m:s): ')

    dist_predict = input('prediction distance (meters, if in miles end with m): ')
    while dist_predict == '': # wait for input
        print('\nerror: missing distance')
        dist_predict = input('prediction distance (meters, if in miles end with m): ')

    # convert input distances from mi to km if necessary
    # and evaluate
    if dist_perform[-1] == 'm':
        dist_perform = eval(dist_perform[0:-1]) * 1609.344
    else:
        dist_perform = eval(dist_perform)
    if dist_predict[-1] == 'm':
        dist_predict = eval(dist_predict[0:-1]) * 1609.344
    else:
        dist_predict = eval(dist_predict)

    # evaluate imput time and calculate total s
    if len(time_perform) <3:
        time_perform = '00:00:' + time_perform
    elif len(time_perform) < 6:
        time_perform = '00:' + time_perform
    time_perform = date.strptime(time_perform, '%H:%M:%S')
    time_seconds = 3600 * time_perform.hour + 60 * time_perform.minute + time_perform.second
    

    # calculate predicted times
    # standard purdy
    time_purdysc_seconds = purdy_standard(time_seconds, dist_perform, dist_predict)
    time_purdysc = time_convert(time_purdysc_seconds)

    # least squares purdy
    time_purdyls_seconds = purdy_leastsq(time_seconds, dist_perform, dist_predict)
    time_purdyls = time_convert(time_purdyls_seconds)
    
    # vo2max
    time_vo2max_seconds = vo2max(time_seconds / 60, dist_perform, dist_predict, time_purdysc_seconds)
    time_vo2max = time_convert(time_vo2max_seconds)
    
    # cameron method
    time_cameron_seconds, perform_offset, predict_offset = cameron(time_seconds, dist_perform / 1609.344, dist_predict / 1609.344)
    time_cameron = time_convert(time_cameron_seconds)

    # reigel method    
    time_reigel_seconds = riegel(time_seconds, dist_perform, dist_predict)
    time_reigel = time_convert(time_reigel_seconds)

    # average of all methods
    time_average_seconds = (time_purdysc_seconds + time_purdyls_seconds + time_vo2max_seconds + time_cameron_seconds + time_reigel_seconds) / 5
    time_average = time_convert(time_average_seconds)
        
    print(('''\npurdy sc: {}
purdy ls: {}
 vo2 max: {}
 cameron: {}
 \tperform valid (0 best): {:5.0f}
 \tpredict valid (0 best): {:5.0f}
  reigel: {}
\n average: {}''').format(time_purdysc, time_purdyls, time_vo2max, time_cameron, perform_offset, predict_offset, time_reigel, time_average))
