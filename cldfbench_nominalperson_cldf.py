import pathlib

from cldfbench import Dataset as BaseDataset
from cldfbench import CLDFWriter as Writer


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "nominalperson_cldf"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        from cldfbench import CLDFSpec
        return CLDFSpec(dir=self.cldf_dir, module='StructureDataset') 
#        return super().cldf_specs()

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw_dir`, e.g.

        >>> self.raw_dir.download(url, fname)
        """
        pass

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.

        >>> args.writer.objects['LanguageTable'].append(...)
        """
        
        with Writer(cldf_spec) as writer:
            for row in self.raw_dir.read_csv(
                'examples.csv',
                dicts=True, 
            ):
                writer.objects['ExampleTable'].append({
                    'ID': row['ID'],
                    'Language_ID': row['Language_ID'],
                    'Primary_Text': row['Primary_Text'],
                    'Analyzed_Word': row['Analyzed_Word'],
                    'Gloss': row['Gloss'],
                    'Translated_Text': row['Translated_Text'],
                    'Meta_Language_ID': row['Meta_Language_ID'],
                    'LGR_Conformance': row['LGR_Conformance'],
                    'Source': row['Source'],
                    'Comments': row['Comments']
                })