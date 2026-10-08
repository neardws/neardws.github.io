from scholarly import scholarly
import json
from datetime import datetime
import os
from pathlib import Path


def generate_citation_data(scholar_id, output_dir='results'):
    author = scholarly.search_author_id(scholar_id)
    scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
    author['updated'] = str(datetime.now())
    author['publications'] = {v['author_pub_id']: v for v in author['publications']}
    print(json.dumps(author, indent=2))

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / 'gs_data.json').open('w', encoding='utf-8') as outfile:
        json.dump(author, outfile, ensure_ascii=False)

    shieldio_data = {
        'schemaVersion': 1,
        'label': 'citations',
        'message': str(author['citedby']),
    }
    with (output_dir / 'gs_data_shieldsio.json').open('w', encoding='utf-8') as outfile:
        json.dump(shieldio_data, outfile, ensure_ascii=False)


def main():
    generate_citation_data(os.environ['GOOGLE_SCHOLAR_ID'])


if __name__ == '__main__':
    main()
