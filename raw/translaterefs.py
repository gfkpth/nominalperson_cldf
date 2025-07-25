# This script is only needed for slightly simplifying preprocessing the creation of the bibtex keys for the Sources field
# the created columns need manual fixes afterwards, so this script is not necessary for regular use, but kept here for reference

import pandas as pd


def bibify_source(regsource):
    '''function for converting references to standard format for bibtex employed here
    
    input: 
    - regsource: a string containing regular references in Name (Year) format, multiple entries separated by semicola
        e.g. "Halle & Marantz (1993: 244); Siddiqi (2011); Schönlein (2026)"
    
    returns:
    - sourcelist: list of entries in normalised format (e.g. ["hallemarantz1993[244]";"siddiqi2011";"schoenlein2026"])
    - qbased: the index of grammar sources that are based on the Comrie & Smith (1977) questionnaire  
    
    '''
    # define list of correspondences for potential special characters in the input
    specialsigns = {'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss',
        'ć': 'c',
        'č': 'c'}
    qbased = None                                 # variable to indicate index of any entry that is based on a questionnaire-based grammar
    
    if not isinstance(regsource, str) or pd.isna(regsource):
        return ''
    
    sourcelist = regsource.split(';')           # split input string at semicola into list of sources
    for i in range(len(sourcelist)):            # iterate through all entries in the list
        sourcelist[i]=sourcelist[i].split(':',1)  # colon separates potential page or section references, split this off; limit to one split (further colons retained inside square brackets)
        sourcelist[i][0]=sourcelist[i][0].replace(r' ','').replace(r'&','').replace(r'.','').replace(r'-','').lower() # normalise author/year reference by removing all commas, ampersands, hyphens and full stops and turn into lower case 
        
        for special in specialsigns:          # convert special signs
            if special in sourcelist[i][0]:
                sourcelist[i][0] = sourcelist[i][0].replace(special,specialsigns[special])
                
        if '(q)' in sourcelist[i][0]:                               # save index of source with marker (q), indicating that it's a reference to a grammar based on the Comrie & Smith questionnaire
            qbased = i
            sourcelist[i][0] = sourcelist[i][0].replace('(q)','')   # remove '(q)' afterwards
        
        # format output by joining normalised references and possible page numbers into one string
        if len(sourcelist[i]) == 2:              # in case there was a colon followed by page information
            sourcelist[i][1] = sourcelist[i][1].strip()   # get rid of extra spaces
            sourcelist[i]='['.join(sourcelist[i])+']'   # join reference and page infos, put latter in square brackets 
        elif len(sourcelist[i]) > 2:            #  the code above should only split for the first colon in a reference and sourcelist should have two items at maximum; this is just to issue a warning in case any more splits took place by accident
            print(f'Warning: reference {sourcelist[i]} contains more than one colon, automatic conversion to bibformat skipped.')
        else:
            sourcelist[i]=sourcelist[i][0]              # flatten references without second part
            
    return ';'.join(sourcelist)


# load csv
df = pd.read_csv('grammarchecks.csv')

# create transformed columns
df['refs_bib'] = df['refs'].apply(bibify_source) 
df['PPDC_refs_bib'] = df['PPDC_ref'].apply(bibify_source) 

# write resulting table
df.to_csv('grammarchecks-bibified.csv')