SCRIPT_ID='spatial_score_slider_build_v20261024T050357Z'
import argparse,json,os,shlex,shutil,struct,subprocess,sys,tempfile,zipfile
from pathlib import Path
PROJECT_VERSION='20261024T050357Z'
METADATA_RELATIVE='Documents/json/SpatialScoreSlider_project_v20261024T050357Z.json'
def run(args):
    cmd=[str(x) for x in args]
    print('$ '+' '.join(shlex.quote(x) for x in cmd),flush=True)
    subprocess.run(cmd,check=True)
def require(cmd):
    path=shutil.which(cmd)
    if not path: raise RuntimeError('Missing '+cmd+' on PATH; install its Termux package.')
    return path
def find_android_jar():
    roots=[os.environ.get('ANDROID_HOME'),os.environ.get('ANDROID_SDK_ROOT'),str(Path.home()/'android-sdk'),str(Path.home()/'Android'/'Sdk'),str(Path(os.environ.get('PREFIX','/data/data/com.termux/files/usr'))/'share'/'android-sdk')]
    jars=[]
    for value in roots:
        if not value: continue
        for jar in (Path(value)/'platforms').glob('android-*/android.jar'):
            try: api=int(jar.parent.name.removeprefix('android-'))
            except ValueError: continue
            if api>=34: jars.append((api,jar))
    if not jars: raise RuntimeError('Android SDK API 34+ android.jar not found; expected $HOME/android-sdk/platforms/android-35/android.jar')
    return max(jars,key=lambda item:item[0])[1]
def align_apk_python(source,destination):
    with zipfile.ZipFile(source,'r') as src,zipfile.ZipFile(destination,'w',allowZip64=True) as dst:
        for old in src.infolist():
            if old.is_dir(): continue
            info=zipfile.ZipInfo(old.filename,date_time=old.date_time)
            info.compress_type=old.compress_type
            info.external_attr=old.external_attr
            info.extra=old.extra
            info.create_system=old.create_system
            if info.compress_type==zipfile.ZIP_STORED:
                filename_size=len(info.filename.encode('utf-8'))
                pad=(4-(dst.fp.tell()+30+filename_size+len(info.extra)+4)%4)%4
                info.extra+=struct.pack('<HH',0xD935,pad)+b'\0'*pad
            dst.writestr(info,src.read(old),compress_type=info.compress_type)
def stage(storage,workspace,metadata):
    stage_dir=workspace/'stage'
    stage_dir.mkdir(parents=True,exist_ok=True)
    for src,relative in metadata['sources'].items():
        origin=storage/src
        if not origin.is_file(): raise FileNotFoundError('Missing source: '+str(origin))
        destination=stage_dir/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(origin,destination)
    print('Staged',len(metadata['sources']),'source files in',stage_dir,flush=True)
    return stage_dir
def build(output_storage,workspace,staged):
    aapt2=require('aapt2')
    javac=require('javac')
    d8=require('d8')
    apksigner=require('apksigner')
    keytool=require('keytool')
    android_jar=find_android_jar()
    compiled=workspace/'compiled'
    generated=workspace/'generated'
    classes=workspace/'classes'
    dex=workspace/'dex'
    for folder in (compiled,generated,classes,dex): folder.mkdir(parents=True,exist_ok=True)
    run([aapt2,'compile','--dir',staged/'res','-o',compiled])
    flats=sorted(compiled.glob('*.flat'))
    if not flats: raise RuntimeError('AAPT2 generated no compiled resources')
    unsigned=workspace/'unsigned.apk'
    run([aapt2,'link','-o',unsigned,'-I',android_jar,'--manifest',staged/'AndroidManifest.xml','--java',generated,'--min-sdk-version','24','--target-sdk-version','34',*flats])
    sources=sorted((staged/'src').rglob('*.java'))+sorted(generated.rglob('*.java'))
    if not sources: raise RuntimeError('No Java source files staged')
    run([javac,'-source','8','-target','8','-encoding','UTF-8','-classpath',android_jar,'-d',classes,*sources])
    bytecode=sorted(classes.rglob('*.class'))
    if not bytecode: raise RuntimeError('No compiled class files found')
    run([d8,'--min-api','24','--lib',android_jar,'--output',dex,*bytecode])
    dexfile=dex/'classes.dex'
    if not dexfile.is_file(): raise RuntimeError('D8 did not generate classes.dex')
    with zipfile.ZipFile(unsigned,'a') as archive: archive.write(dexfile,'classes.dex',compress_type=zipfile.ZIP_STORED)
    aligned=workspace/'aligned.apk'
    zipalign=shutil.which('zipalign')
    if zipalign: run([zipalign,'-f','4',unsigned,aligned])
    else: align_apk_python(unsigned,aligned)
    key=Path.home()/'.android'/'debug.keystore'
    key.parent.mkdir(parents=True,exist_ok=True)
    if not key.exists(): run([keytool,'-genkeypair','-keystore',key,'-alias','androiddebugkey','-storepass','android','-keypass','android','-keyalg','RSA','-keysize','2048','-validity','10000','-dname','CN=Android Debug,O=Android,C=US'])
    signed=workspace/'signed.apk'
    run([apksigner,'sign','--ks',key,'--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--min-sdk-version','24','--out',signed,aligned])
    run([apksigner,'verify','--verbose','--print-certs',signed])
    destination=output_storage/'Documents'/'apk'/('SpatialScoreSlider_rebuilt_v'+PROJECT_VERSION+'.apk')
    destination.parent.mkdir(parents=True,exist_ok=True)
    fd,temp_name=tempfile.mkstemp(prefix='.spatial-score-slider_',suffix='.tmp',dir=str(destination.parent))
    os.close(fd)
    temp_path=Path(temp_name)
    try:
        shutil.copyfile(signed,temp_path)
        if temp_path.stat().st_size!=signed.stat().st_size: raise RuntimeError('APK copy size mismatch')
        os.replace(temp_path,destination)
    finally:
        temp_path.unlink(missing_ok=True)
    print('APK:',destination,flush=True)
    return destination
def main():
    parser=argparse.ArgumentParser(description='Build Spatial Score Slider with temporary sources and automatic cleanup')
    parser.add_argument('--storage-root',default='/storage/emulated/0')
    parser.add_argument('--output-root',default='/storage/emulated/0')
    parser.add_argument('--install',action='store_true')
    args=parser.parse_args()
    storage=Path(args.storage_root).expanduser().resolve()
    output=Path(args.output_root).expanduser().resolve()
    metadata=json.loads((storage/METADATA_RELATIVE).read_text(encoding='utf-8'))
    if metadata.get('script_id')!=SCRIPT_ID: raise RuntimeError('Project metadata does not match this build script')
    with tempfile.TemporaryDirectory(prefix='spatial_score_slider_build_') as temp:
        workspace=Path(temp)
        staged=stage(storage,workspace,metadata)
        apk=build(output,workspace,staged)
    if args.install:
        run([require('termux-open'),'--view','--content-type','application/vnd.android.package-archive',apk])
        print('Complete installation in the Android system installer.',flush=True)
if __name__=='__main__':
    try: main()
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as exc:
        print('BUILD FAILED:',exc,file=sys.stderr)
        sys.exit(1)
