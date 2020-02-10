irradiation_array = [[0,235,354,531,668,751,819], [0,247,399,525,653,775,825],
                    [0,230,301,502,623,725,807], [0,228,295,467,612,714,767],
                    [0,199,287,423,546,590,752], [0,155,272,408,483,582,624],
                    [0,152,233,359,425,574,599], [0,129,169,311,367,387,475],
                    [0,62,109,178,196,219,270]]

def angle_to_col(num):
    #columns: <0	0-20	21-30	31-40	41-50	51-60	61-90
    if num <= 0:
        return 0
    if num <= 20:
        return 1
    if num <= 30:
        return 2
    if num <= 40:
        return 3
    if num <= 50:
        return 4
    if num <= 60:
        return 5
    if num <= 91:
        return 6
    raise Exception('angle should be between -90 and 90. {} invalid'.format(num))

def perc_to_okta(num):
    if 0 <= num and num <= 100:
        return ceil(8*num/100)
    else:
        raise Exception('percent should be between 0 and 100. {} invalid'.format(num))

#takes cloud cover as a percentage and altitude angle in degrees
def get_irradiation(cloud_cover, altitude_angle):
    i = perc_to_okta(cloud_cover)
    j = angle_to_col(altitude_angle)
    return irradiation_array[i][j]
