import re
import pathlib
import json

from cldfbench import Dataset as BaseDataset
from cldfzenodo import Record


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "nominalperson_cldf"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        from cldfbench import CLDFSpec
        return CLDFSpec(dir=self.cldf_dir, module='Generic')  # As long as we don't add values.
        return CLDFSpec(dir=self.cldf_dir, module='StructureDataset')

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw_dir`, e.g.

        >>> self.raw_dir.download(url, fname)
        """
        
        # download WALS dataset
        wals_dir = self.raw_dir / 'wals'
        if not wals_dir.exists():
            wals_dir.mkdir()
        rec = Record.from_doi('10.5281/zenodo.13950591')
        rec.download_dataset(wals_dir)

    def cmd_makecldf(self, args):
        # Extend the schema:
        args.writer.cldf.add_component(
            'LanguageTable',
            'Walscode',
            {'name': 'ISOcodes', 'separator': ';', 'datatype': {'base': 'string', 'format': '[a-z]{3}'}}        # pre-coded ISO639P3code doesn't allow multiple values, but we have exceptional cases with two alternative iso codes
            )
        args.writer.cldf.add_component('ExampleTable','Source')

        args.writer.cldf.add_component('CodeTable')
        args.writer.cldf.add_component('ParameterTable')
        args.writer.cldf.add_component('ValueTable','Examples')

        # load glottocodes
        print('Loading glottocodes')
        glangs = {lg.id: lg for lg in args.glottolog.api.languoids()}
        print('Done\n')

        # loading parameters and code descriptions from parameter-codes.json
        print('Loading parameters and codes')
        with open(self.raw_dir.joinpath('parameter-codes.json')) as parameters_file:
            param_dict = json.load(parameters_file)
        
        print('Done\n')

                
        # extract WALS features of interest from parameters dictionary so the appropriate values are loaded from WALS
        # The relevant features are characterised in parameter-codes.json by containing a `wals_param` value with the name of the relevant WALS table.
        # Those entries contain no other content specification, which is instead extracted from the WALS dataset directly.
        # 
        # (for now these are 83A (verb-object order), 85A (adposition order), 86A (genitive order) and 88A (demonstrative order))
        print('Loading WALS data and extracting relevant parameters')
        wals_foi = [param_dict[param]['wals_param'] for param in param_dict if 'wals_param' in param_dict[param]]
        
        # WALS uses different feature names from the ones employed in grammarchecks.csv
        # option 1a: use the _wals columns from grammarchecks.csv, where the features names are already adapted
        # option 1b: translate WALS features to the terminology of the corresponding features in grammarchecks
        # option 2: import the feature definitions from WALS wholesale
        #
        # going with option 2 for now, as it potentially makes extending the database with additional data easier,
        # since available WALS values can be automatically integrated that way
        
        # create a dictionary for WALS codes (mappings of CLDF-WALS-internal code and feature name)
        wals_codes = {}
        for r in self.raw_dir.joinpath('wals').read_csv('codes.csv', dicts=True):
            wals_codes[r['ID']] = r['Name']                                 # first, create dictionary for WALS codes
            if r['Parameter_ID'] in wals_foi:                               # AND for the rows relevant to factors of interest
                for param in param_dict:                                     # find the WALS-related entries in param_dict
                    if 'wals_param' in param_dict[param] and param_dict[param]['wals_param'] == r['Parameter_ID']:
                        if 'values' not in param_dict[param]:                # ensure 'values' exists
                            param_dict[param]['values'] = {}
                            
                        param_dict[param]['values'][r['Name']] = r['Description']    # and add the WALS value definitions to the param_dict entry
                                            
        # create dictionary mapping features of interest to dictionaries mapping wals language codes to their value for that feature 
        wals_dict = {
            feature: {
                r['Language_ID']: wals_codes[r['Code_ID']]
                for r in self.raw_dir.joinpath('wals').read_csv('values.csv', dicts=True)
                if r['Parameter_ID'] == feature} 
            for feature in wals_foi                                    # list of the features of interest      
        }
        print('Done\n')
        
        # write parameter and code tables based on param_dict
        for param in param_dict.keys():
            args.writer.objects['ParameterTable'].append(dict(
                ID=param,
                Name=param.replace('_', ' '),
                Description=param_dict[param]['descr']
            ))
            for code in param_dict[param]['values'].keys():  
                args.writer.objects['CodeTable'].append(dict(
                    ID=param + code.replace(' ',''),
                    Parameter_ID=param,
                    Name=code,
                    Description=param_dict[param]['values'][code]
                ))

        # load data from grammarchecks
        print('Loading data from grammarchecks.csv and writing LanguageTable')
        lids = {}           # working dictionary for looking up language ids given a glottocode
        values_dict = {}    # working dictionary for values table
        lang_id=0           # counter for assigning unique language IDs
        val_id=0            # counter for assigning unique value IDs
        for row in self.raw_dir.read_csv('grammarchecks.csv',dicts=True):
#            if row['verb_object_order_wals']:
#                assert row['verb_object_order_wals'] == wals_83A[row['walscode']], '{}: {} vs. {}'.format(row['walscode'], row['verb_object_order_wals'], wals_83A[row['walscode']])
            # Print warning in case the table row has a glottocode not found in the glottolog dataset - this could indicate a typo in the source dataset.
            # However, it could also be a case of no glottocode being assigned (yet) for a languagevariety
            if row['glottocode'] not in glangs:
                print('Warning, glottocode [', row['glottocode'], '] not found in glottolog for language', row['lang_name'])    
            # save working copy of correspondences of glottocode with tuples of lang_id and language name
            # in case there is no glottocode for some reason, use the language name as index as a workaround for completeness
            # slight inconsistency is not optimal, but should be no problem because this is mostly needed for looking up language IDs for the example list 
            if row['glottocode'] == '' or not row['glottocode']:
                lids[row['lang_name']]=(lang_id,row['lang_name']) 
            else:
                lids[row['glottocode']]=(lang_id,row['lang_name']) 
            
            if row['lat']: 
                lat=row['lat']
    #        else: 
    #            lat=args.glottolog.api.languoids.Languoid(id_=row['glottocode']).latitude
    
            # write languages table
            args.writer.objects['LanguageTable'].append({
                'ID': lang_id,
                'Name': row['lang_name'] ,
                'Macroarea': row['area_glottolog'],
                'Latitude': lat,
                'Longitude': row['lon'],
                'Glottocode': row['glottocode'],
                'ISOcodes': sorted(set(re.findall(r'[a-z]{3}', row['iso639_3']))),
                'Walscode': row['walscode']
            })
            
            # extract sources on nominal person if available
            if row['refs'] != '':
                nompers_sources,nompers_qindex = self.bibify_source(row['refs'])
            # extract sources on PPDCs
            if row['PPDC_ref'] != '':
                ppdc_sources,ppdc_qindex = self.bibify_source(row['PPDC_ref'])
                
            
            for param in param_dict.keys():
                match param:
                    # load WALS values fresh from the WALS dataset for consistency and extensibility (instead of the pre-extracted ones in the source dataset)
                    case x if 'wals' in x:                                # if current parameter contains the keyword "wals", i.e. is a WALS version        
                        if row['walscode'] in wals_dict[param_dict[param]['wals_param']]:  # check if there is a WALS value available for that feature for the language under consideration 
                            val = wals_dict[param_dict[param]['wals_param']][row['walscode']]
                            # add data to working dictionary of values table                        
                            values_dict[val_id]={'Language_ID': lang_id,  #row['glottocode'],
                                                 'Parameter_ID': param,
                                                 'Value': val,
                                                 'Code_ID': param + val.replace(' ','')
                                                 }
                        else:
                            continue                                                    # if there's no WALS data available, consider next parameter
                    # for values concerning nominal person also include the listed sources
                    case x if param_dict[x].get('person-rel') and row[x] in param_dict[param]['values']:    
                        
                        val = row[param]
                        # distinct sources available for PPDC
                        if param == 'PPDC':     
                            # add data to working dictionary of values table                        
                            values_dict[val_id]={'Language_ID': lang_id,    #row['glottocode'],
                                                'Parameter_ID': param,
                                                'Value': val,
                                                'Code_ID': param + val.replace(' ',''),
                                                'Source': ppdc_sources
                            }
                        # otherwise provide general nominal person sources
                        else:
                            # add data to working dictionary of values table                        
                            values_dict[val_id]={'Language_ID': lang_id,    #row['glottocode'],
                                                    'Parameter_ID': param,
                                                    'Value': val,
                                                    'Code_ID': param + val.replace(' ',''),
                                                    'Source': nompers_sources
                                                }
                    # for all other, non-person-related parameters only add value lines if there is a value:  
                    case x if not param_dict[x].get('person-rel') and row[param] != '':                               
                        
                        val = row[param]
                        # add data to working dictionary of values table                        
                        values_dict[val_id]={'Language_ID': lang_id,    #row['glottocode'],
                                                'Parameter_ID': param,
                                                'Value': val,
                                                'Code_ID': param + val.replace(' ','')
                                            }
                        
                val_id+=1   # increase val_id counter after successful entry
            
            lang_id+=1      # increase lang_id counter finishing entries for language

        print('Done\n')

        # load data from examples.csv
        print('Reading examples.csv')
        for row in self.raw_dir.read_csv('examples.csv',dicts=True):
            
            # check if the example gloss contains a determiner
            # if so, set a flag to mark the example as relevant for PPDC 
            # (Somewhat simplistic, a more detailed treatment could be considered later)
            contains_ppdc = False
            if 'DEM' in row['Gloss']:
                contains_ppdc = True
            
            # find the entry in lang_id based on the glottocode under Language_ID
            # return the first value of the corresponding tuple, which is the independent language ID assigned above
            if lids.get(row['Language_ID']) == None:
                print(f"Couldn't resolve language ID for {row['Language_Name']} with glottocode {row['Language_ID']}. Check manually please.")
                continue
            else:
                current_lang_id = lids.get(row['Language_ID'])[0]
                
                
            # do the same lookup for the meta language of translation
            if lids.get(row['Meta_Language_ID']) == None:
                print(f"Couldn't resolve language ID for metalanguage with glottocode {row['Meta_Language_ID']} when processing example from {row['Language_Name']}. Check manually please.")
                continue
            else:
                meta_lang_id = lids.get(row['Meta_Language_ID'])[0]            

            # enter row into ExampleTable
            args.writer.objects['ExampleTable'].append({
                'ID': row['ID'],
                'Language_ID': current_lang_id,      
                'Primary_Text': row['Primary_Text'],
                'Analyzed_Word': row['Analyzed_Word'].split(),
                'Gloss': row['Gloss'].split(),
                'Translated_Text': row['Translated_Text'],
                'Meta_Language_ID': meta_lang_id,
                'LGR_Conformance': row['LGR_Conformance'],
                'Comment': row['Comment'],
                'Source': row['Source']                    
            })
            
            
            # iterate through values_dict to add example IDs where appropriate
            for val in values_dict:
                # only consider value data rows concerning the current language and involving person-related parameters
                if values_dict[val]['Language_ID'] == current_lang_id and param_dict[values_dict[val]['Parameter_ID']].get('person-rel'):
                        # if there is no Examples field yet, create one
                        if values_dict[val].get('Examples') == None:
                            values_dict[val]['Examples'] = []
                        
                        # add example IDs to all value rows that are not PPDC and to PPDC if there is 
                        if values_dict[val].get('Parameter_ID') != 'PPDC' or contains_ppdc:
                            # add example ID to values_dict entry
                            values_dict[val]['Examples'].append(row['ID'])  

        print('Done\n')

        # write ValuesTable
        print('Writing ValuesTable')
        for val in values_dict:
            if values_dict[val].get('Source') and values_dict[val].get('Examples'):
                args.writer.objects['ValueTable'].append({
                                'ID': val,
                                'Language_ID': values_dict[val]['Language_ID'],
                                'Parameter_ID': values_dict[val]['Parameter_ID'],
                                'Value': values_dict[val]['Value'],
                                'Code_ID': values_dict[val]['Code_ID'],
                                'Source': values_dict[val]['Source'],
                                'Examples': ';'.join(values_dict[val]['Examples'])      
                                })
            elif values_dict[val].get('Source') and not values_dict[val].get('Examples'):
                args.writer.objects['ValueTable'].append({
                                'ID': val,
                                'Language_ID': values_dict[val]['Language_ID'],
                                'Parameter_ID': values_dict[val]['Parameter_ID'],
                                'Value': values_dict[val]['Value'],
                                'Code_ID': values_dict[val]['Code_ID'],
                                'Source': values_dict[val]['Source'],
                                'Examples': ''                         
                                })
            elif (not values_dict[val].get('Source')) and values_dict[val].get('Examples'):
                args.writer.objects['ValueTable'].append({
                                'ID': val,
                                'Language_ID': values_dict[val]['Language_ID'],
                                'Parameter_ID': values_dict[val]['Parameter_ID'],
                                'Value': values_dict[val]['Value'],
                                'Code_ID': values_dict[val]['Code_ID'],
                                'Source': '',
                                'Examples': ';'.join(values_dict[val]['Examples'])
                                })
            else:
                args.writer.objects['ValueTable'].append({
                                'ID': val,
                                'Language_ID': values_dict[val]['Language_ID'],
                                'Parameter_ID': values_dict[val]['Parameter_ID'],
                                'Value': values_dict[val]['Value'],
                                'Code_ID': values_dict[val]['Code_ID'],
                                'Source': '',
                                'Examples': ''
                                })
        
        print('Done\n')
        
        
        
    def bibify_source(self, regsource):
        '''function for converting references to standard format for bibtex employed here
        
        input: 
        - regsource: a string containing regular references in Name (Year) format, multiple entries separated by semicola
          e.g. "Halle & Marantz (1993: 244); Siddiqi (2011); Schönlein (2026)"
        
        returns:
        - sourcelist: list of entries in normalised format (e.g. ["hallemarantz1993[244]";"siddiqi2011";"schoenlein2026"])
        - qbased: the index of any source that is based on 
        
        '''
        # define list of correspondences for potential special characters in the input
        specialsigns = {'ä': 'ae',
            'ö': 'oe',
            'ü': 'ue',
            'ß': 'ss',
            'ć': 'c',
            'č': 'c'}
        qbased = None                                 # variable to indicate index of any entry that is based on a questionnaire-based grammar
        
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
                
        return sourcelist,qbased   