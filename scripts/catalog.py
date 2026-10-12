"""Catálogo portable: biblioteca estándar de Python 3.10+, sin depender del T7."""
import argparse,copy,csv,datetime,json,os,re,shutil,sys,unicodedata,urllib.parse,urllib.request,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'data/catalog.json'
def today():return datetime.date.today().isoformat()
def read(path=DEFAULT):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(data,path=DEFAULT):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(path)
def norm(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).strip()
def validate(data,check_assets=False):
    if data.get('schemaVersion')!=1:raise ValueError('schemaVersion debe ser 1')
    seen=set();identities=set();tmdb=set()
    for x in data['items']:
        if not x.get('id') or x['id'] in seen:raise ValueError('ID vacío o repetido')
        seen.add(x['id'])
        if not x.get('title') or x.get('type') not in ['movies','series']:raise ValueError('Título o tipo inválido')
        if x.get('year') and not re.fullmatch(r'\d{4}',str(x['year'])):raise ValueError('Año inválido')
        ident=(x['type'],norm(x['title']),str(x.get('year') or ''))
        if ident in identities:raise ValueError('Título/año repetido: '+x['title'])
        identities.add(ident)
        m=x.get('meta',{})
        if m.get('tmdb'):
            k=(x['type'],m['tmdb'])
            if k in tmdb:raise ValueError('TMDB repetido')
            tmdb.add(k)
        for key in ['poster','backdrop','source','trailer']:
            value=m.get(key)
            if not value:continue
            if not value.startswith('https://') and not (key in ['poster','backdrop'] and re.fullmatch(r'assets/[a-zA-Z0-9_-]+\.(jpg|png|webp)',value)):
                raise ValueError('URL o ruta inválida: '+key)
            if check_assets and value.startswith('assets/') and not (ROOT/'web'/value).is_file():raise ValueError('Falta imagen: '+value)
        for f in x.get('files',[]):
            if 'path' in f:raise ValueError('Las rutas del disco no se publican')
            if any(e in f.get('name','').lower() for e in ['.mkv','.avi','.mp4']):raise ValueError('No se publican los nombres originales de vídeo')
    return data
def add(data,title,year=None,media_type='movies',location='Sin especificar',note='',metadata=None):
    m=metadata or {'matched':False,'title':title,'genres':[],'director':[],'cast':[],'synopsis':'','source':None}
    title=m.get('title') or title;year=m.get('year') or year
    for old in data['items']:
        if (old['type'],norm(old['title']),str(old.get('year') or ''))==(media_type,norm(title),str(year or '')) or (m.get('tmdb') and old['type']==media_type and old['meta'].get('tmdb')==m['tmdb']):
            raise ValueError('La película/serie ya existe: '+old['title'])
    x={'id':'manual-'+uuid.uuid4().hex[:12],'title':title,'type':media_type,'year':str(year) if year else None,'files':[],'bytes':None,'meta':m,'inventory':{'source':'manual','location':location,'note':note,'recordedAt':today()}}
    data['items'].append(x);data['updated']=today();validate(data);return x
def api(endpoint,params=None):
    key=os.environ.get('TMDB_API_KEY') or os.environ.get('TMDB_ACCESS_TOKEN')
    if not key:raise ValueError('Configura TMDB_API_KEY o TMDB_ACCESS_TOKEN en el entorno, o añade sin TMDB')
    params={'language':'es-ES',**(params or {})};headers={'User-Agent':'CineT7Catalogo/1.0'}
    if len(key)>70:headers['Authorization']='Bearer '+key
    else:params['api_key']=key
    try:
        with urllib.request.urlopen(urllib.request.Request('https://api.themoviedb.org/3/'+endpoint+'?'+urllib.parse.urlencode(params),headers=headers),timeout=30) as response:return json.load(response)
    except Exception:raise ValueError('TMDB no ha respondido correctamente; no se guardó el cambio') from None
def metadata(tmdb_id,media_type):
    typ='tv' if media_type=='series' else 'movie';d=api(f'{typ}/{tmdb_id}',{'append_to_response':'credits,videos,external_ids'})
    trailers=[v for v in d.get('videos',{}).get('results',[]) if v.get('site')=='YouTube' and v.get('type')=='Trailer']
    return {'matched':True,'tmdb':d['id'],'imdb':d.get('imdb_id') or d.get('external_ids',{}).get('imdb_id'),'title':d.get('title') or d.get('name'),'original':d.get('original_title') or d.get('original_name'),'year':(d.get('release_date') or d.get('first_air_date') or '')[:4] or None,'synopsis':d.get('overview',''),'genres':[g['name'] for g in d.get('genres',[])],'runtime':d.get('runtime'),'rating':d.get('vote_average'),'votes':d.get('vote_count'),'tagline':d.get('tagline',''),'country':', '.join(c['name'] for c in d.get('production_countries',[])),'director':[c['name'] for c in d.get('credits',{}).get('crew',[]) if c.get('job')=='Director'] or [c['name'] for c in d.get('created_by',[])],'cast':[c['name'] for c in d.get('credits',{}).get('cast',[])[:10]],'poster':'https://image.tmdb.org/t/p/w500'+d['poster_path'] if d.get('poster_path') else None,'backdrop':'https://image.tmdb.org/t/p/w1280'+d['backdrop_path'] if d.get('backdrop_path') else None,'source':f'https://www.themoviedb.org/{typ}/{d["id"]}','trailer':'https://www.youtube.com/watch?v='+trailers[0]['key'] if trailers else None,'checkedAt':today()}
def sanitize_import(data):
    out={'schemaVersion':1,'updated':today(),'scanned':data.get('scanned'),'volume':data.get('volume','Colección'),'items':[]}
    for x in data['items']:
        files=[]
        for i,f in enumerate(x.get('files',[]),1):
            files.append({'name':f'Temporada {f["season"]}, capítulo {f["episode"]}' if f.get('season') else f'Copia {i}','bytes':f.get('bytes'),'season':f.get('season'),'episode':f.get('episode'),'technical':f.get('technical',{})})
        m={k:v for k,v in x.get('meta',{}).items() if k not in ['posterRemote','backdropRemote','query','identificationNote','confidence']}
        m.setdefault('checkedAt',data.get('scanned'))
        out['items'].append({'id':str(x['id']),'title':x['title'],'type':x['type'],'year':str(x['year']) if x.get('year') else None,'files':files,'bytes':x.get('bytes'),'meta':m,'inventory':x.get('inventory',{'source':'scan','location':data.get('volume','T7'),'recordedAt':data.get('scanned'),'note':''})})
    return out
def merge_import(data,incoming):
    incoming=sanitize_import(incoming);count=0
    for x in incoming['items']:
        old=next((o for o in data['items'] if o['type']==x['type'] and ((x['meta'].get('tmdb') and x['meta']['tmdb']==o['meta'].get('tmdb')) or (norm(o['title'])==norm(x['title']) and str(o.get('year'))==str(x.get('year'))))),None)
        if old:
            old['files']=x['files'];old['bytes']=x['bytes'];old['inventory']['source']='scan';old['inventory']['recordedAt']=incoming.get('scanned');old['inventory']['location']=x['inventory']['location']
        else:
            if any(o['id']==x['id'] for o in data['items']):x['id']='import-'+uuid.uuid4().hex[:12]
            data['items'].append(x)
        count+=1
    data['scanned']=incoming.get('scanned');data['updated']=today();validate(data);return count
def build(data,destination):
    validate(data,check_assets=True);destination=Path(destination).resolve()
    if destination!=ROOT/'dist':raise ValueError('La salida de publicación debe ser dist/ dentro del repo')
    destination.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'web',destination,dirs_exist_ok=True)
    write(data,destination/'catalog.json');(destination/'.nojekyll').touch()
    with (destination/'listado-peliculas.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['Título','Año','Tipo','Ubicación','Origen','Archivos escaneados','Fuente de ficha'])
        for x in data['items']:w.writerow([x['title'],x.get('year') or '',x['type'],x['inventory']['location'],x['inventory']['source'],len(x['files']),x['meta'].get('source') or 'Pendiente'])
    (destination/'listado-peliculas.txt').write_text('\n'.join(f'{x["title"]} ({x.get("year") or "sin año"}) — {x["inventory"]["location"]}' for x in data['items']),encoding='utf-8')
    return destination
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--catalog',type=Path,default=DEFAULT);sub=p.add_subparsers(dest='cmd',required=True)
    for cmd in ['validate','build']:sub.add_parser(cmd)
    a=sub.add_parser('add');a.add_argument('--title',required=True);a.add_argument('--year',type=int);a.add_argument('--type',choices=['movies','series'],default='movies');a.add_argument('--location',default='Sin especificar');a.add_argument('--note',default='');a.add_argument('--tmdb-id',type=int);a.add_argument('--metadata-file',type=Path)
    u=sub.add_parser('update');u.add_argument('--id',required=True);u.add_argument('--location');u.add_argument('--note');u.add_argument('--tmdb-id',type=int)
    r=sub.add_parser('remove');r.add_argument('--id',required=True)
    s=sub.add_parser('search');s.add_argument('--title',required=True);s.add_argument('--year',type=int);s.add_argument('--type',choices=['movies','series'],default='movies')
    i=sub.add_parser('import');i.add_argument('--file',type=Path,required=True)
    args=p.parse_args();data=read(args.catalog)
    if args.cmd=='validate':validate(data,True);print(f'OK: {len(data["items"])} títulos')
    elif args.cmd=='build':print(build(data,ROOT/'dist'))
    elif args.cmd=='search':
        typ='tv' if args.type=='series' else 'movie';params={'query':args.title}
        if args.year:params['year' if typ=='movie' else 'first_air_date_year']=args.year
        for x in api('search/'+typ,params).get('results',[])[:8]:print(x['id'],x.get('title') or x.get('name'),x.get('release_date') or x.get('first_air_date'))
    elif args.cmd=='add':
        meta=metadata(args.tmdb_id,args.type) if args.tmdb_id else read(args.metadata_file) if args.metadata_file else None
        x=add(data,args.title,args.year,args.type,args.location,args.note,meta);write(data,args.catalog);print('Añadida: '+x['title']+' · '+x['id'])
    elif args.cmd=='update':
        x=next((x for x in data['items'] if x['id']==args.id),None)
        if not x:raise ValueError('No existe ese ID')
        if args.location is not None:x['inventory']['location']=args.location
        if args.note is not None:x['inventory']['note']=args.note
        if args.tmdb_id:x['meta']=metadata(args.tmdb_id,x['type']);x['title']=x['meta']['title'];x['year']=x['meta']['year']
        data['updated']=today();validate(data);write(data,args.catalog);print('Actualizado: '+x['title'])
    elif args.cmd=='remove':
        if not any(x['id']==args.id for x in data['items']):raise ValueError('No existe ese ID')
        data['items']=[x for x in data['items'] if x['id']!=args.id];data['updated']=today();write(data,args.catalog);print('Título eliminado')
    elif args.cmd=='import':print('Registros incorporados:',merge_import(data,read(args.file)));write(data,args.catalog)
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError) as error:print('Error: '+str(error),file=sys.stderr);sys.exit(1)
