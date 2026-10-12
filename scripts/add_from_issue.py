import json,os,re
from pathlib import Path
from catalog import read,write,add
def fields(body):
    out={}
    for m in re.finditer(r'^### ([^\n]+)\n\n(.*?)(?=\n### |\Z)',body.replace('\r\n','\n'),re.M|re.S):
        value=m[2].strip();out[m[1]]=None if value in ['', '_No response_'] else value
    return out
def process(data,event):
    issue=event['issue'];owner=event['repository']['owner']['login']
    if issue['user']['login']!=owner:raise ValueError('Solo el propietario puede añadir títulos automáticamente')
    f=fields(issue.get('body') or '')
    if not f.get('Título'):raise ValueError('Falta el título en el formulario')
    year=f.get('Año')
    if year and not re.fullmatch(r'\d{4}',year):raise ValueError('El año debe tener cuatro cifras')
    return add(data,f['Título'],year,'series' if f.get('Tipo')=='Serie' else 'movies',f.get('Ubicación') or 'Sin especificar',f.get('Comentario') or '')
if __name__=='__main__':
    event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text());data=read()
    try:process(data,event);write(data)
    except ValueError as e:
        if 'ya existe' not in str(e):raise
        print(e)
    with open(os.environ['GITHUB_ENV'],'a') as out:out.write('ISSUE_NUMBER='+str(int(event['issue']['number']))+'\n')
