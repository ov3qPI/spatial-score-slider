SCRIPT_ID='spatial_score_slider_release_v20261024T052630Z'
import argparse,fcntl,getpass,hashlib,json,os,runpy,secrets,shlex,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
VERSION='v1.0.0'
PACKAGE='cc0.KPYQrT.spatialscoreslider'
PASS_ENV='SPATIAL_SCORE_SLIDER_RELEASE_PASS'
META='Documents/json/SpatialScoreSlider_project_v20261024T050357Z.json'
BUILDER='Documents/py/spatial_score_slider_build_v20261024T050357Z.py'
KEY_ALIAS='spatial-score-slider'
def signing_credentials(keytool):
    folder=Path.home()/'.android'
    folder.mkdir(mode=0o700,parents=True,exist_ok=True)
    key=folder/'SpatialScoreSlider_release_cc0.KPYQrT.spatialscoreslider.p12'
    passfile=folder/'SpatialScoreSlider_release_cc0.KPYQrT.spatialscoreslider.pass'
    lock=folder/'SpatialScoreSlider_release_cc0.KPYQrT.spatialscoreslider.lock'
    with lock.open('a+') as guard:
        lock.chmod(0o600)
        fcntl.flock(guard,fcntl.LOCK_EX)
        if key.is_file() and not passfile.is_file():
            if not sys.stdin.isatty(): raise RuntimeError('Existing release key requires one-time password migration in an interactive terminal; key not modified')
            previous=getpass.getpass('Existing release keystore password (one-time migration): ')
            if not previous: raise RuntimeError('Empty password; existing key not modified')
            env=os.environ.copy()
            env[PASS_ENV]=previous
            subprocess.run([keytool,'-list','-keystore',str(key),'-storetype','PKCS12','-storepass:env',PASS_ENV,'-alias',KEY_ALIAS],check=True,env=env,stdout=subprocess.DEVNULL)
            password=previous
            save_password(passfile,password)
            print('Existing release key preserved; password saved privately for future unattended signing.',flush=True)
        elif not passfile.is_file():
            password=secrets.token_urlsafe(48)
            save_password(passfile,password)
            print('Generated and privately stored a random release signing password.',flush=True)
        password=passfile.read_text(encoding='ascii').rstrip('\n')
        if len(password)<6: raise RuntimeError('Saved release password is invalid; refusing to modify the signing key')
        passfile.chmod(0o600)
        env=os.environ.copy()
        env[PASS_ENV]=password
        if not key.exists():
            fd,temp_path=tempfile.mkstemp(prefix='.spatial-release-',suffix='.p12',dir=folder)
            os.close(fd)
            tmp=Path(temp_path)
            tmp.unlink()
            try:
                print('Generating the new release signing key in',folder,flush=True)
                subprocess.run([keytool,'-genkeypair','-keystore',str(tmp),'-storetype','PKCS12','-alias',KEY_ALIAS,'-storepass:env',PASS_ENV,'-keypass:env',PASS_ENV,'-keyalg','RSA','-keysize','3072','-validity','10000','-dname','CN=Spatial Score Slider,OU=CC0,O=KPYQrT'],check=True,env=env)
                tmp.chmod(0o600)
                os.replace(tmp,key)
            finally: tmp.unlink(missing_ok=True)
        elif not key.is_file(): raise RuntimeError('Release signing path exists but is not a file')
        key.chmod(0o600)
        subprocess.run([keytool,'-list','-keystore',str(key),'-storetype','PKCS12','-storepass:env',PASS_ENV,'-alias',KEY_ALIAS],check=True,env=env,stdout=subprocess.DEVNULL)
        print('Signing credentials: existing keystore reused, credentials never printed during the build.',flush=True)
        return key,env
def save_password(path,password):
    fd,filename=tempfile.mkstemp(prefix='.spatial-release-pass-',dir=path.parent)
    temp=Path(filename)
    try:
        with os.fdopen(fd,'w',encoding='ascii') as out:
            out.write(password+'\n')
            out.flush()
            os.fsync(out.fileno())
        temp.chmod(0o600)
        if path.exists(): raise RuntimeError('Refusing to overwrite existing signing password')
        os.replace(temp,path)
    finally: temp.unlink(missing_ok=True)
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
    key,env=signing_credentials(require('keytool'))
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
    print('BACKUP: keystore and password are stored in ~/.android/; preserve both to maintain update compatibility.',flush=True)
if __name__=='__main__':
    try: main()
    except (OSError,RuntimeError,ValueError,KeyError,subprocess.CalledProcessError) as exc:
        print('RELEASE BUILD FAILED:',exc,file=sys.stderr)
        sys.exit(1)
