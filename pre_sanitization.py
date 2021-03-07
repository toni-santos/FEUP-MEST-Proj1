import pandas as pd
import numpy as np
import matplotlib.pylab as plt

def calculate_age(yymm):
    """
    Receives the date of birth in the format yymm and calculates the current age
    related to the time of donation
    """
    strym = str(yymm)

    if strym == '0':
        return np.nan
    
    elif len(strym) < 4:
        while len(strym) < 4:
            strym = '0' + strym

    year = 1900 + int(strym[:2])
    month = int(strym[2:])

    if month > 6:
        return 1997 - year
    else:
        return 1997 - year + 1




def get_definite_age(subset):
    """
    Calculates the age of the person based on the AGEFLAG field (which will choose the origin of the age)
    """

    final_ages = []

    for item, frame in subset["AGEFLAG"].iteritems():
        if pd.notnull(frame):
            if frame == 'E':
                final_ages.append(subset["AGE"][item])
            elif frame == 'I':
                date = calculate_age(subset["DOB"][item])
                final_ages.append(date)
        else:
            age = subset["AGE"][item]
            dob = calculate_age(subset["DOB"][item])
            # Appends age if it exists and dob doesn't
            if pd.notnull(age) and dob == np.nan:
                final_ages.append(age)
            # Appends dob if it exists and age doesn't
            elif pd.notnull(dob) and age == np.nan:
                final_ages.append(dob)
            # If both exists, appends them if they are equal and, if they're not
            # nan is appended, since it is most likely an error that would be mirrored on our data
            elif pd.notnull(age) and pd.notnull(dob):
                if age == dob:
                    final_ages.append(age)
                else:
                    final_ages.append(np.nan)
            # If none exists, appends nan
            else:
                final_ages.append(np.nan)

    return final_ages


def parse_domain(domain):
    """
    Receives the DOMAIN field in the format yymm
    and turns it into 2 different fiels with each byte
    """

    byte1, byte2 = [], []
    for item in domain:
        if len(item) == 2:
            byte1.append(item[0])
            byte2.append(item[1])
        else:
            byte1.append(np.nan)
            byte2.append(np.nan)
    return byte1, byte2


def lastgif_curr_diff(yymm):
    """
    Return the number of months between the date of the donation
    and the date of the last donation
    """
    strym = str(yymm)
    
    year = 1900 + int(strym[:2])
    month = int(strym[2:])

    if year < 1997:
        return 12 * (1997 - year) + 6

    elif year == 1997:
        return 6 - month


def parse_mdmaud(mdmaud):

    freq, amnt = [],[]
    for item in mdmaud:
        if item == "XXXX":
            freq.append(np.nan)
            amnt.append(np.nan)
        else:
            freq.append(item[1])
            amnt.append(item[2])
    return freq,amnt

if __name__ == '__main__':

    #Data sets

    dataset = ['dev.csv', 'comp.csv']

    #File path

    FILE_PATH = f'./files/{dataset[1]}'


    #Parsing the excel sheet with pandas
    if FILE_PATH[-3:] == 'sxl':
        data = pd.read_excel(FILE_PATH)
    #Parsing .csv files with pandas
    else:    
        data = pd.read_csv(FILE_PATH)

# TODO:              maybe use CLUSTER

    #Colums we didn't found useful
    cols_to_remove = ["ODATEDW", "STATE", "ZIP", "MAILCODE", "CLUSTER", "HOMEOWNR"
                      , "CHILD03", "CHILD07", "CHILD12", "CHILD18", "GENDER"
                      , "MBCRAFT", "MBGARDEN", "MBBOOKS", "MBCOLECT", "MAGFAML"
                      , "MAGFEM", "MAGMALE", "PUBGARDN", "PUBCULIN", "PUBCULIN"
                      , "PUBHLTH", "PUBDOITY", "PUBNEWFN", "PUBPHOTO", "PUBOPP"
                      , "NGIFTALL", "CARDGIFT", "MINRAMNT", "MINRDATE", "MAXRAMNT"
                      , "MAXRDATE", "LASTGIFT", "FISTDATE", "NEXTDATE"
                      , "TIMELAG", "AVGGIFT", "CLUSTER2", "GEOCODE2"]

    #Columns we found useful
    cols_to_use = ["DOB", "AGE", "AGEFLAG" "MDMAUD", "DOMAIN", "LASTDATE"
                   , "NUMCHLD", "INCOME", "WEALTH", "HIT", "NGIFTALL"
                   , "CONTROLN", "TARGET_B"]

    #Removing cols_to_remove

    data.drop(cols_to_remove, axis = 1, inplace = True)

    ###DATE FIELDS PRE-PROCESSING

    data["AGEFLAG"].replace(' ', np.nan, inplace=True)


    ages_fields = ["DOB", "AGE", "AGEFLAG"]

    ages_subset = data[ages_fields]


    ages = get_definite_age(ages_subset)

    data.drop(ages_fields , axis=1, inplace=True)    
    data.insert(2, "AGE", ages)

    ###DOMAIN BYTES PRE-PROCESSING

    domain_byte1, domain_byte2 = parse_domain(data["DOMAIN"])

    data.drop("DOMAIN", axis=1, inplace=True)

    data.insert(2, "UCITY", domain_byte1)
    data.insert(2, "SESNEI", domain_byte2)


    timediff = [lastgif_curr_diff(item) for item in data["LASTDATE"]]

    data.insert(4, "TIMEDIFF", timediff)

    ###MDMAUD PRE-PROCESSING

    ## TODO: PLS LOOK AT THIS IDK IF IT FUNFATES WELL

    freqgiv, amntgiv = parse_mdmaud(data["MDMAUD"])

    data.drop("MDMAUD", axis=1, inplace=True)

    data.insert(2, "FREQGIV", freqgiv)
    data.insert(2, "AMNTGIV", amntgiv)

    print(data)
    ### EXPORT TO .csv

    # pd.DataFrame.to_csv(data, "/home/gui1612/dev/FEUP-MEST-Proj1/comp_sanitized.csv", index=False)
