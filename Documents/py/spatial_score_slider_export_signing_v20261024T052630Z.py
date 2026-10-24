SCRIPT_ID='spatial_score_slider_export_signing_v20261024T052630Z'
import base64,hashlib,sys,textwrap
from pathlib import Path
KEY_ALIAS='spatial-score-slider'
PACKAGE='cc0.KPYQrT.spatialscoreslider'
def main():
    folder=Path.home()/'.android'
    key=folder/'SpatialScoreSlider_release_cc0.KPYQrT.spatialscoreslider.p12'
    passfile=folder/'SpatialScoreSlider_release_cc0.KPYQrT.spatialscoreslider.pass'
    if not key.is_file() or not passfile.is_file(): raise RuntimeError('Signing credentials not found. First build the release to create them automatically.')
    pw=passfile.read_text(encoding='ascii').strip()
    blob=key.read_bytes()
    print('<SpatialScoreSlider_Release_Credentials>')
    print('Package: '+PACKAGE)
    print('KeyAlias: '+KEY_ALIAS)
    print('KeystoreType: PKCS12')
    print('KeystoreLocation: '+str(key))
    print('PasswordLocation: '+str(passfile))
    print('KeystorePassword: '+pw)
    print('KeystoreSHA256: '+hashlib.sha256(blob).hexdigest())
    print('KeystoreBase64:')
    for line in textwrap.wrap(base64.b64encode(blob).decode('ascii'),76): print(line)
    print('</SpatialScoreSlider_Release_Credentials>')
if __name__=='__main__':
    try: main()
    except (OSError,RuntimeError,UnicodeError) as exc:
        print('CREDENTIAL EXPORT FAILED:',exc,file=sys.stderr)
        sys.exit(1)
