import copy,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import catalog
from add_from_issue import process
class CatalogTests(unittest.TestCase):
    def setUp(self):self.data={'schemaVersion':1,'updated':'2026-10-12','items':[]}
    def test_manual_title_without_disk_has_no_invented_measurements(self):
        x=catalog.add(self.data,'Título de prueba',2020,location='DVD')
        self.assertEqual(x['files'],[]);self.assertIsNone(x['bytes']);self.assertEqual(x['inventory']['source'],'manual');self.assertFalse(x['meta']['matched']);catalog.validate(self.data)
    def test_duplicate_and_remake(self):
        catalog.add(self.data,'Una película',1980)
        with self.assertRaises(ValueError):catalog.add(self.data,'UNA PELICULA',1980)
        catalog.add(self.data,'Una película',2020)
        self.assertEqual(len(self.data['items']),2)
    def test_import_preserves_manual_title_and_removes_paths(self):
        manual=catalog.add(self.data,'Mi película',2020,location='DVD')
        incoming={'scanned':'2026-10-12','items':[{'id':'disk-1','title':'Otra película','type':'movies','year':'1999','bytes':100,'files':[{'name':'release.mkv','path':'D:/pelis/release.mkv','bytes':100,'technical':{'width':1920}}],'meta':{'matched':False}}]}
        catalog.merge_import(self.data,incoming)
        self.assertEqual(self.data['items'][0]['id'],manual['id']);self.assertNotIn('path',self.data['items'][1]['files'][0]);self.assertEqual(self.data['items'][1]['files'][0]['name'],'Copia 1');catalog.validate(self.data)
    def test_owner_issue_is_data_not_shell_code(self):
        event={'issue':{'number':1,'user':{'login':'owner'},'body':'### Título\n\nTítulo $(no_ejecutar)\n\n### Año\n\n2020\n\n### Tipo\n\nPelícula\n\n### Ubicación\n\nDVD\n\n### Comentario\n\n_No response_'},'repository':{'owner':{'login':'owner'}}}
        x=process(self.data,event);self.assertEqual(x['title'],'Título $(no_ejecutar)');self.assertEqual(x['inventory']['location'],'DVD')
        event['issue']['user']['login']='stranger'
        with self.assertRaises(ValueError):process(self.data,event)
    def test_public_inventory_valid_and_complete(self):
        data=catalog.read();catalog.validate(data,True)
        self.assertTrue(data['items'])
        for x in data['items']:
            if x.get('bytes') is not None:self.assertEqual(x['bytes'],sum(f['bytes'] for f in x['files']))
        raw=json.dumps(data)
        for private_marker in ['C:\\\\Users','D:\\\\','api_key','Bearer ','@estrenoscine','nocturniap2p','.mkv','.avi']:
            self.assertNotIn(private_marker,raw)
if __name__=='__main__':unittest.main()
