import json
import requests

from config import *


__all__ = ['get_text']


def ocr_space_file(bfile, overlay=False, api_key='', language='eng'):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': api_key,
        'language': language,
    }

    r = requests.post('https://api.ocr.space/parse/image', files={'img.png': bfile}, data=payload)
    return r.content.decode()


def get_text(bfile):
    data = ocr_space_file(bfile, overlay=True, api_key=OCR['api_key'])

    results = json.loads(data)

    try:
        return results['ParsedResults'][0]['ParsedText']
    except (KeyError, IndexError):
        return None


if __name__ == '__main__':
    # FIXME: Rudimentary manual testing
    import sys
    fname = sys.argv[1]
    with open(fname, 'rb') as f:
        t = get_text(f.read())
        print(t)
