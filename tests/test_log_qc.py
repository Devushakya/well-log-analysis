import unittest
import pandas as pd
from scripts.log_qc import inspect_logs

class QualityTests(unittest.TestCase):
    def test_missing_and_sort(self):
        df=pd.DataFrame({'WELL':['A','A','B'],'DEPTH_MD':[2,1,3],'GR':[-999.25,50,90]})
        rows,report=inspect_logs(df,'A')
        self.assertEqual(rows.DEPTH_MD.tolist(),[1,2])
        self.assertEqual(report.iloc[0].missing_pct,50)
    def test_unknown_well(self):
        with self.assertRaises(ValueError):
            inspect_logs(pd.DataFrame({'WELL':['A'],'DEPTH_MD':[1],'GR':[20]}),'B')

if __name__=='__main__': unittest.main()
