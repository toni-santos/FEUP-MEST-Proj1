import pandas as pd
import numpy as np


def calculate_age(yymm):
    """
    Receives the date of birth in the format yymm and calculates the current age
    in relation to the date when of the fund raising occurred
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
    If the ageflag is 'E' the age comes directly from the age field and if it is 'I' we calculate it based on the DOB field.
    If the ageflag has no value we check both fields and make sure DOB and AGE display the same value. 
    If so, we use it. If they don't match, we place a NaN
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
    Receives the DOMAIN field and turns it into
    2 different fields, each one containg a different
    DOMAIN byte
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
    Returns the number of months between the 
    date of the fund raising and the date of
    the last donation
    """

    strym = str(yymm)
    
    year = 1900 + int(strym[:2])
    month = int(strym[2:])

    if year < 1997:
        return 12 * (1996 - year) + (12 - month) + 6 

    elif year == 1997:
        return 6 - month


def parse_mdmaud(mdmaud):
    """
    Parses MDMAUD field into 2 different fields (FREQ and AMNT),
    which, respectively, contain the 2nd and 3rd bytes of MDMAUD
    """

    freq, amnt = [], []
    for item in mdmaud:
        if item == "XXXX":          #The donor is not a major donor
            freq.append(np.nan)
            amnt.append(np.nan)
        else:
            freq.append(item[1])    #2nd byte -> Frequency of giving
            amnt.append(item[2])    #3rd byte -> Amount of giving
    return freq, amnt



if __name__ == '__main__':

    #Data sets

    dataset = ['dev.csv', 'comp.csv']

    #File path

    FILE_PATH = f'./given_files/{dataset[1]}'


    #Parsing the excel sheet with pandas
    if FILE_PATH[-3:] == 'sxl':
        data = pd.read_excel(FILE_PATH)
    #Parsing .csv files with pandas
    else:    
        data = pd.read_csv(FILE_PATH)

    #Colums we didn't found useful (Columns in this list will be removed)
    cols_to_remove = ["ODATEDW", "ZIP", "MAILCODE"
                      , "CHILD03", "CHILD07", "CHILD12", "CHILD18"
                      , "MBCRAFT", "MBGARDEN", "MBBOOKS", "MBCOLECT", "MAGFAML"
                      , "MAGFEM", "MAGMALE", "PUBGARDN", "PUBCULIN", "PUBCULIN"
                      , "PUBHLTH", "PUBDOITY", "PUBNEWFN", "PUBPHOTO", "PUBOPP"
                      , "NGIFTALL", "CARDGIFT", "MINRAMNT", "MINRDATE", "MAXRAMNT"
                      , "MAXRDATE", "FISTDATE", "NEXTDATE"
                      , "CLUSTER2", "GEOCODE2"]

    #Columns we found useful (This list won't affect the code, but it is more comprehensible)

    cols_to_use = ["DOB", "STATE", "CLUSTER", "AGE", "AGEFLAG" "MDMAUD", "DOMAIN", "LASTDATE"
                   , "NUMCHLD", "INCOME", "WEALTH", "HIT", "NGIFTALL", "LASTGIFT", "TIMELAG"
                   , "CONTROLN", "TARGET_B", "AVGGIFT", "HOMEOWNR", "GENDER", "RAMNTALL"]

    #Removing cols_to_remove

    data.drop(cols_to_remove, axis = 1, inplace = True)

    ###DATE FIELDS PRE-PROCESSING

    data["AGEFLAG"].replace(' ', np.nan, inplace=True)


    ages_fields = ["DOB", "AGE", "AGEFLAG"]

    ages_subset = data[ages_fields]


    ages = get_definite_age(ages_subset)

    data.drop(ages_fields , axis=1, inplace=True)    
    data.insert(1, "AGE", ages)

    ###DOMAIN BYTES PRE-PROCESSING

    domain_byte1, domain_byte2 = parse_domain(data["DOMAIN"])

    
    #data.drop("DOMAIN", axis=1, inplace=True)

    data.insert(1, "UCITY", domain_byte1)
    data.insert(1, "SESNEI", domain_byte2)

    ###TIME BETWEEN LAST DONATION AND CURRENT DATE

    timediff = [lastgif_curr_diff(item) for item in data["LASTDATE"]]

    data.insert(1, "TIMEDIFF", timediff)

    ### MDMAUD PRE-PROCESSING (at the moment we are not using MDMAUD, as we are parsing it with Rapid Minner)  

    #freqgiv, amntgiv = parse_mdmaud(data["MDMAUD"])

    #data.drop("MDMAUD", axis=1, inplace=True)

    #data.insert(1, "FREQGIV", freqgiv)
    #data.insert(1, "AMNTGIV", amntgiv)

    # Tests (Uncomment the line bellow)  
    print(data)

    ### EXPORT TO .csv

    file_name = "comp_sanitized.csv"        # Name of the file to be exported

    pd.DataFrame.to_csv(data, f"./sanitized_files/{file_name}", index=False)