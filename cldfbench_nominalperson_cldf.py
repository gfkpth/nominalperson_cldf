import pathlib
import itertools

from cldfbench import Dataset as BaseDataset
from cldfbench import CLDFWriter as Writer


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
        pass

    def cmd_makecldf(self, args):
        # Extend the schema:
        args.writer.cldf.add_component('LanguageTable')
        args.writer.cldf.add_columns('LanguageTable','Walscode')    # add non-standard column
        
        args.writer.cldf.add_component('CodeTable')
        args.writer.cldf.add_component('ParameterTable')
        args.writer.cldf.add_component('ValueTable')
        args.writer.cldf.add_component('ExampleTable')

        # Load data from grammarchecks
        
        lang_id=0
        val_id=0
        for row in self.raw_dir.read_csv('grammarchecks.csv',dicts=True):
            if row['include']=='y':
                args.writer.objects['LanguageTable'].append({
                    'ID': row['glottocode'],
                    'Name': row['lang_name'] ,
                    'Macroarea': row['area_glottolog'],
                    'Latitude': row['lat'],
                    'Longitude': row['lon'],
                    'Glottocode': row['glottocode'],
                    'ISO639P3code': row['iso639_3'],
                    'Walscode': row['walscode']
                })
                args.writer.objects['ValueTable'].append({
                    'ID': val_id,
                    'Language_ID': row['glottocode'],
                    'Parameter_ID': 'APC Order',
                    'Value': row['apc_order']
                })
                val_id+=1
                args.writer.objects['ValueTable'].append({
                    'ID': val_id,
                    'Language_ID': row['glottocode'],
                    'Parameter_ID': 'Constituent Order',
                    'Value': row['constituent_order']
                })
                val_id+=1
            
            
 #       for lid, rows in itertools.groupby(
 #           sorted(
 #               self.raw_dir.read_csv('examples.csv', dicts=True),
 #               key=lambda row: (row['Language_ID'], int(row['ID']))),
 #           lambda row: row['Language_ID']
 #       ):
 #           rows = list(rows)
 #           args.writer.objects['LanguageTable'].append(dict(
 #               ID=lid,
 #               Name=rows[0]['Language_Name'],
 #           ))
 #           for row in rows:
            for row in self.raw_dir.read_csv('examples.csv',dicts=True):
                args.writer.objects['ExampleTable'].append({
                    'ID': row['ID'],
                    'Language_ID': row['Language_ID'],
                    'Primary_Text': row['Primary_Text'],
                    'Analyzed_Word': row['Analyzed_Word'].split(),
                    'Gloss': row['Gloss'].split(),
                    'Translated_Text': row['Translated_Text'],
                    'Meta_Language_ID': row['Meta_Language_ID'],
                    'LGR_Conformance': row['LGR_Conformance'],
                    'Source': row['Source'],
                    'Comments': row['Comment']
                })
        

