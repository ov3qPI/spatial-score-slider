SCRIPT_ID='spatial_score_slider_release_v20261024T051252Z'
import argparse,getpass,hashlib,json,os,runpy,shlex,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
VERSION='v1.0.0'
PACKAGE='cc0.KPYQrT.spatialscoreslider'
PASS_ENV='SPATIAL_SCORE_SLIDER_RELEASE_PASS'
META='Documents/json/SpatialScoreSlider_project_v20261024T050357Z.json'
BUILDER='Documents/py/spatial_score_slider_build_v20261024T050357Z.py'
KEY_ALIAS='spatial-score-slider'
def main():
    p=argparse.ArgumentParser(description='Build a separately release-signed Spatial Score Slider APK using the source-only Termux repository')
    p.add_argument('--repo-root',required=True)
    p.add_argument('--output-root',default='/storage/emulated/0')
    a=p.parse_args()
    root=Path(a.repo_root).expanduser().resolve()
    output=Path(a.output_root).expanduser().resolve()
    meta=json.loads((root/META).read_text(encoding='utf-8'))
    if meta.get('package')!=PACKAGE: raise RuntimeError('Unexpected Android package ID in project metadata')
    manifest=root/next(x for x,y in meta['sources'].items() if y=='AndroidManifest.xml')
    data=ET.parse(manifest).getroot()
    ns='{http://schemas.android.com/apk/res/android}'
    if data.get('package')!=PACKAGE or data.get(ns+'versionCode')!='1' or data.get(ns+'versionName')!='1.0': raise RuntimeError('Manifest package/version mismatch for v1.0.0')
    build=runpy.run_path(str(root/BUILDER))
    run=build['run']
    require=build['require']
    keytool=require('keytool')
    key=Path.home()/'.android'/'SpatialScoreSlider_release_cc0.KPYQrT.spatialscoreslider.p12'
    key.parent.mkdir(parents=True,exist_ok=True)
    os.umask(0o077)
    if not sys.stdin.isatty(): raise RuntimeError('Interactive terminal required to unlock the release signing key')
    password=getpass.getpass('Release keystore password: ')
    if len(password)<12: raise RuntimeError('Use a release signing password of at least 12 characters')
    env=os.environ.copy()
    env[PASS_ENV]=password
    if key.exists():
        subprocess.run([keytool,'-list','-keystore',str(key),'-storetype','PKCS12','-storepass:env',PASS_ENV,'-alias',KEY_ALIAS],check=True,env=env,stdout=subprocess.DEVNULL)
    else:
        if getpass.getpass('Confirm new release password: ')!=password: raise RuntimeError('Passwords do not match; signing key not created')
        print('Generating persistent release signing key at',key,flush=True)
        subprocess.run([keytool,'-genkeypair','-keystore',str(key),'-storetype','PKCS12','-alias',KEY_ALIAS,'-storepass:env',PASS_ENV,'-keypass:env',PASS_ENV,'-keyalg','RSA','-keysize','3072','-validity','10000','-dname','CN=Spatial Score Slider,OU=CC0,O=KPYQrT'],check=True,env=env)
        key.chmod(0o600)
    del password
    aapt2=require('aapt2')
    javac=require('javac')
    d8=require('d8')
    apksigner=require('apksigner')
    android_jar=build['find_android_jar']()
    with tempfile.TemporaryDirectory(prefix='spatial_score_slider_release_') as td:
        workspace=Path(td)
        stage=build['stage'](root,workspace,meta)
        compiled=workspace/'compiled'
        generated=workspace/'generated'
        classes=workspace/'classes'
        dex=workspace/'dex'
        for folder in (compiled,generated,classes,dex): folder.mkdir(parents=True,exist_ok=True)
        run([aapt2,'compile','--dir',stage/'res','-o',compiled])
        flats=sorted(compiled.glob('*.flat'))
        if not flats: raise RuntimeError('No AAPT2 resource output')
        unsigned=workspace/'unsigned.apk'
        run([aapt2,'link','-o',unsigned,'-I',android_jar,'--manifest',stage/'AndroidManifest.xml','--java',generated,'--min-sdk-version','24','--target-sdk-version','34',*flats])
        source_files=sorted((stage/'src').rglob('*.java'))+sorted(generated.rglob('*.java'))
        if not source_files: raise RuntimeError('No Java sources')
        run([javac,'-source','8','-target','8','-encoding','UTF-8','-classpath',android_jar,'-d',classes,*source_files])
        bytecode=sorted(classes.rglob('*.class'))
        if not bytecode: raise RuntimeError('No compiled classes')
        run([d8,'--min-api','24','--lib',android_jar,'--output',dex,*bytecode])
        dex_file=dex/'classes.dex'
        if not dex_file.is_file(): raise RuntimeError('D8 generated no classes.dex')
        with zipfile.ZipFile(unsigned,'a') as z: z.write(dex_file,'classes.dex',compress_type=zipfile.ZIP_STORED)
        aligned=workspace/'aligned.apk'
        zipalign=shutil.which('zipalign')
        if zipalign: run([zipalign,'-f','4',unsigned,aligned])
        else: build['align_apk_python'](unsigned,aligned)
        signed=workspace/'release.apk'
        sign_args=[apksigner,'sign','--ks',key,'--ks-type','PKCS12','--ks-key-alias',KEY_ALIAS,'--ks-pass','env:'+PASS_ENV,'--key-pass','env:'+PASS_ENV,'--min-sdk-version','24','--out',signed,aligned]
        print('$ '+' '.join(shlex.quote(str(x)) for x in sign_args),flush=True)
        subprocess.run([str(x) for x in sign_args],check=True,env=env)
        run([apksigner,'verify','--verbose','--print-certs',signed])
        dest=output/'Documents'/'apk'/('SpatialScoreSlider_'+VERSION+'.apk')
        dest.parent.mkdir(parents=True,exist_ok=True)
        fd,filename=tempfile.mkstemp(prefix='.spatial-score-slider-release-',suffix='.tmp',dir=dest.parent)
        os.close(fd)
        tmp=Path(filename)
        try:
            shutil.copyfile(signed,tmp)
            if tmp.stat().st_size!=signed.stat().st_size: raise RuntimeError('Final APK copy size mismatch')
            os.replace(tmp,dest)
        finally: tmp.unlink(missing_ok=True)
    env.pop(PASS_ENV,None)
    print('RELEASE_APK:',dest,flush=True)
    print('SHA256:',hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
    print('SIGNING_KEY:',key,flush=True)
    print('Preserve the keystore and password for all future updates.',flush=True)
if __name__=='__main__':
    try: main()
    except (OSError,RuntimeError,ValueError,KeyError,subprocess.CalledProcessError) as exc:
        print('RELEASE BUILD FAILED:',exc,file=sys.stderr)
        sys.exit(1)
