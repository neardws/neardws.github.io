"""
Fetches CCF Class A conference deadlines from ccfddl/ccf-deadlines.
Categories: DS (Computer Architecture), NW (Network System),
            AI (Artificial Intelligence), HI (Computer-Human Interaction)
Outputs: assets/data/cfp.json
"""

import os
import json
import requests
import yaml
from datetime import datetime, timezone, timedelta

CATEGORIES = ['DS', 'NW', 'AI', 'HI']
CATEGORY_NAMES = {
    'DS': 'Computer Architecture',
    'NW': 'Network System',
    'AI': 'Artificial Intelligence',
    'HI': 'Computer-Human Interaction',
}
BASE_API = 'https://api.github.com/repos/ccfddl/ccf-deadlines/contents/conference'
HEADERS = {'Accept': 'application/vnd.github.v3+json'}


def parse_timezone(tz_str):
    """Convert timezone string to a timezone object."""
    if tz_str is None:
        return timezone.utc
    tz_str = str(tz_str).strip()
    if tz_str == 'AoE':
        return timezone(timedelta(hours=-12))
    if tz_str == 'UTC':
        return timezone.utc
    if tz_str.startswith('UTC+'):
        try:
            offset = float(tz_str[4:])
            return timezone(timedelta(hours=offset))
        except ValueError:
            return timezone.utc
    if tz_str.startswith('UTC-'):
        try:
            offset = float(tz_str[4:])
            return timezone(timedelta(hours=-offset))
        except ValueError:
            return timezone.utc
    return timezone.utc


def parse_deadline(deadline_str, tz):
    """Parse a deadline string into a timezone-aware datetime."""
    if not deadline_str:
        return None
    s = str(deadline_str).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d'):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=tz)
        except ValueError:
            continue
    return None


def get_best_conf_entry(confs, now_utc):
    """
    Scan all conference-year entries and their timelines.
    Returns (conf_entry, timeline_entry, is_future) for:
      - the nearest future deadline, or
      - the most recent past deadline if none future.
    """
    future_candidates = []
    past_candidates = []

    for conf in confs:
        tz = parse_timezone(conf.get('timezone', 'UTC'))
        for tl in conf.get('timeline', []):
            deadline_str = tl.get('deadline')
            if not deadline_str:
                continue
            dt = parse_deadline(deadline_str, tz)
            if dt is None:
                continue
            dt_utc = dt.astimezone(timezone.utc)
            if dt_utc > now_utc:
                future_candidates.append((dt_utc, conf, tl))
            else:
                past_candidates.append((dt_utc, conf, tl))

    if future_candidates:
        future_candidates.sort(key=lambda x: x[0])
        _, conf, tl = future_candidates[0]
        return conf, tl, True

    if past_candidates:
        past_candidates.sort(key=lambda x: x[0], reverse=True)
        _, conf, tl = past_candidates[0]
        return conf, tl, False

    return None, None, False


def fetch_category_files(category):
    """Return list of file objects for YAML files in a category directory."""
    url = f'{BASE_API}/{category}'
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        print(f'  Warning: Could not fetch {url} (HTTP {resp.status_code})')
        return []
    return [
        f for f in resp.json()
        if f.get('name', '').endswith(('.yaml', '.yml'))
    ]


def fetch_yaml(download_url):
    """Download and parse a YAML file; returns list of conference dicts."""
    resp = requests.get(download_url, timeout=30)
    if resp.status_code != 200:
        return []
    try:
        data = yaml.safe_load(resp.text)
    except yaml.YAMLError:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def main():
    now_utc = datetime.now(timezone.utc)
    future_list = []
    past_list = []

    for category in CATEGORIES:
        print(f'Processing category {category} ({CATEGORY_NAMES[category]})...')
        files = fetch_category_files(category)
        print(f'  Found {len(files)} YAML files')

        for file_info in files:
            entries = fetch_yaml(file_info['download_url'])
            for entry in entries:
                # Filter: CCF rank must be 'A'
                rank = entry.get('rank', {})
                ccf_rank = (
                    str(rank.get('ccf', '')).strip()
                    if isinstance(rank, dict)
                    else str(rank).strip()
                )
                if ccf_rank != 'A':
                    continue

                confs = entry.get('confs', [])
                if not confs:
                    continue

                conf_entry, tl_entry, is_future = get_best_conf_entry(confs, now_utc)
                if conf_entry is None:
                    continue

                record = {
                    'title': entry.get('title', ''),
                    'description': entry.get('description', ''),
                    'sub': category,
                    'sub_name': CATEGORY_NAMES[category],
                    'ccf_rank': ccf_rank,
                    'link': conf_entry.get('link', '') or '',
                    'abstract_deadline': tl_entry.get('abstract_deadline') or None,
                    'deadline': tl_entry.get('deadline') or None,
                    'timezone': str(conf_entry.get('timezone', 'UTC')),
                    'date': conf_entry.get('date', '') or '',
                    'place': conf_entry.get('place', '') or '',
                    'year': conf_entry.get('year'),
                    'is_future': is_future,
                }

                # Stringify deadline values for consistent JSON
                if record['deadline'] is not None:
                    record['deadline'] = str(record['deadline'])
                if record['abstract_deadline'] is not None:
                    record['abstract_deadline'] = str(record['abstract_deadline'])

                if is_future:
                    future_list.append(record)
                else:
                    past_list.append(record)

    # Sort future by nearest deadline first
    future_list.sort(key=lambda c: c.get('deadline') or '9999-99-99')
    # Sort past by most recent deadline first
    past_list.sort(key=lambda c: c.get('deadline') or '0000-00-00', reverse=True)

    result = {
        'updated_at': now_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'conferences': future_list + past_list,
    }

    os.makedirs('assets/data', exist_ok=True)
    output_path = 'assets/data/cfp.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total = len(future_list) + len(past_list)
    print(f'\nSaved {total} CCF-A conferences to {output_path}')
    print(f'  Future: {len(future_list)}, Past: {len(past_list)}')


if __name__ == '__main__':
    main()
