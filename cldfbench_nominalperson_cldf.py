import re
import pathlib

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
            {'name': 'ISOcodes', 'separator': ';', 'datatype': {'base': 'string', 'format': '[a-z]{3}'}})

        #args.writer.cldf.add_component('CodeTable')
        args.writer.cldf.add_component('ParameterTable')
        args.writer.cldf.add_component('ValueTable')
        args.writer.cldf.add_component('ExampleTable')

        glangs = {lg.id: lg for lg in args.glottolog.api.languoids()}

        wals_codes = {r['ID']: r['Name'] for r in self.raw_dir.joinpath('wals').read_csv('codes.csv', dicts=True)}
        wals_83A = {
            r['Language_ID']: wals_codes[r['Code_ID']]
            for r in self.raw_dir.joinpath('wals').read_csv('values.csv', dicts=True)
            if r['Parameter_ID'] == '83A'}

        params = ['apc_order', 'constituent_order']
        for param in ['apc_order', 'constituent_order']:
            args.writer.objects['ParameterTable'].append(dict(
                ID=param,
                Name=param.replace('_', ' '),
            ))

        # Load data from grammarchecks
        lids = set()
        val_id=0
        for row in self.raw_dir.read_csv('grammarchecks.csv',dicts=True):
            if row['constituent_order_wals']:
                assert row['constituent_order_wals'] == wals_83A[row['walscode']], '{}: {} vs. {}'.format(row['walscode'], row['constituent_order_wals'], wals_83A[row['walscode']])
            if row['include']=='y':
                assert row['glottocode'] in glangs
                lids.add(row['glottocode'])
                args.writer.objects['LanguageTable'].append({
                    'ID': row['glottocode'],
                    'Name': row['lang_name'] ,
                    'Macroarea': row['area_glottolog'],
                    'Latitude': row['lat'],
                    'Longitude': row['lon'],
                    'Glottocode': row['glottocode'],
                    'ISOcodes': sorted(set(re.findall(r'[a-z]{3}', row['iso639_3']))),
                    'Walscode': row['walscode']
                })
                for param in params:
                    args.writer.objects['ValueTable'].append({
                        'ID': val_id,
                        'Language_ID': row['glottocode'],
                        'Parameter_ID': param,
                        'Value': row[param]
                    })
                    val_id+=1

        for row in self.raw_dir.read_csv('examples.csv',dicts=True):
            if row['Language_ID'] in lids:
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
