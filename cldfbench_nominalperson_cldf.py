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
        args.writer.cldf.add_component('ExampleTable')

        for lid, rows in itertools.groupby(
            sorted(
                self.raw_dir.read_csv('examples.csv', dicts=True),
                key=lambda row: (row['Language_ID'], int(row['ID']))),
            lambda row: row['Language_ID']
        ):
            rows = list(rows)
            args.writer.objects['LanguageTable'].append(dict(
                ID=lid,
                Name=rows[0]['Language_Name'],
            ))
            for row in rows:
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
