"""Reviewed official model release metadata, separate from original run evidence."""

from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

# Maker-owned domains and official organization namespaces. New authorities need review.
OFFICIAL_DOMAINS = {
    'OpenAI': ('openai.com',),
    'Anthropic': ('anthropic.com', 'claude.com'),
    'Google': ('google.com', 'blog.google', 'deepmind.google', 'googleblog.com', 'ai.google.dev'),
    'DeepSeek': ('deepseek.com',),
    'xAI': ('x.ai',),
    'Z.ai': ('z.ai', 'zhipuai.cn', 'bigmodel.cn', 'zai-org.github.io'),
    'Tencent': ('tencent.com', 'hunyuan.ai'),
    'Xiaomi': ('xiaomi.com', 'xiaomimimo.com'),
    'Meta': ('meta.com', 'fb.com', 'llama.com', 'research.meta.ai'),
    'Alibaba': ('alibabacloud.com', 'aliyun.com', 'qwen.ai', 'qwenlm.github.io'),
    'Moonshot AI': ('moonshot.ai', 'moonshot.cn', 'kimi.com'),
    'MiniMax': ('minimax.io', 'minimaxi.com'),
}
OFFICIAL_ORGS = {
    'OpenAI': ('openai',), 'Anthropic': ('anthropics',), 'Google': ('google', 'google-deepmind'),
    'DeepSeek': ('deepseek-ai',), 'xAI': ('xai-org',), 'Z.ai': ('zai-org', 'thudm'),
    'Tencent': ('tencent', 'tencent-hunyuan'), 'Xiaomi': ('xiaomimimo',),
    'Meta': ('meta-llama', 'facebookresearch'), 'Alibaba': ('qwen', 'qwenlm'),
    'Moonshot AI': ('moonshotai',), 'MiniMax': ('minimaxai',),
}
# Individually reviewed manufacturer announcements; this does not trust a social host or every post by an account.
OFFICIAL_ANNOUNCEMENTS = {
    'Xiaomi': ('https://x.com/XiaomiMiMo/status/2046988157888209365',),
}
UNKNOWN = {'source_url': None, 'date_basis': 'unknown',
           'notes': {'en': 'Official release date not verified.', 'zh': '尚未核实官方发布日期。'}}


def iso_day(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
        raise ValueError('model release metadata: dates must use YYYY-MM-DD')
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise ValueError('model release metadata: invalid calendar date') from error
    return value


def official_source(vendor, value):
    if not isinstance(value, str) or re.search(r'[\s\\\x00-\x1f\x7f]', value):
        return False
    try:
        url = urlsplit(value)
        if url.scheme != 'https' or not url.hostname or url.username or url.password or url.port:
            return False
    except ValueError:
        return False
    host = url.hostname.lower()
    if value in OFFICIAL_ANNOUNCEMENTS.get(vendor, ()):
        return True
    if any(host == domain or host.endswith('.' + domain) for domain in OFFICIAL_DOMAINS.get(vendor, ())):
        return True
    organization = url.path.split('/')[1] if url.path.startswith('/') else ''
    return host in ('github.com', 'huggingface.co') and organization.lower() in OFFICIAL_ORGS.get(vendor, ())


def load(path, identities):
    path = Path(path)
    if not path.exists():
        return {}
    try:
        snapshot = json.loads(path.read_text())
        if not isinstance(snapshot, dict) or type(snapshot.get('schema_version')) is not int or snapshot['schema_version'] != 1 or not isinstance(snapshot.get('models'), list):
            raise ValueError('invalid schema')
        as_of = iso_day(snapshot.get('as_of'))
        entries = {}
        fields = {'vendor', 'name', 'release_date', 'source_url', 'date_basis', 'notes'}
        for entry in snapshot['models']:
            if not isinstance(entry, dict) or set(entry) != fields:
                raise ValueError('invalid model fields')
            key = entry['vendor'], entry['name']
            if any(not isinstance(value, str) or not value.strip() or value != value.strip() for value in key):
                raise ValueError('invalid model identity')
            if key not in identities or key in entries:
                raise ValueError(f'duplicate or unmatched model identity: {key}')
            notes = entry['notes']
            if not isinstance(notes, dict) or set(notes) != {'en', 'zh'} or any(not isinstance(value, str) or not value.strip() for value in notes.values()):
                raise ValueError(f'{key}: notes need English and Chinese')
            day, basis, source = entry['release_date'], entry['date_basis'], entry['source_url']
            if basis == 'official_release':
                if iso_day(day) > as_of or source is None:
                    raise ValueError(f'{key}: release needs a source and cannot follow the review date')
            elif basis != 'unknown' or day is not None:
                raise ValueError(f'{key}: unknown release dates must stay null')
            if source is not None and not official_source(entry['vendor'], source):
                raise ValueError(f'{key}: source must be a reviewed maker-owned HTTPS URL')
            entries[key] = entry
        return entries
    except (ValueError, KeyError, TypeError) as error:
        raise ValueError(f'model release metadata: {error}') from error


def attach(runs, path):
    entries = load(path, {(run['vendor'], run['name']) for run in runs})
    for run in runs:
        entry = entries.get((run['vendor'], run['name']))
        run['model_release_date'] = entry['release_date'] if entry else None
        run['model_release'] = {field: entry[field] for field in ('source_url', 'date_basis', 'notes')} if entry else {
            **UNKNOWN, 'notes': dict(UNKNOWN['notes']),
        }


def sort_key(run):
    day = run.get('model_release_date')
    return (day is None, -int(day.replace('-', '')) if day else 0, run['vendor'], run['name'])
