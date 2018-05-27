# coding=utf-8
'''
数据相关视图
'''

from config import media_prefix
try:
    from html import escape  # python 3.x
except ImportError:
    from cgi import escape  # python 2.x


def title_html(fullkey, sid, db):
    out = '''
    <h2>%(fullkey)s
          <a class="btn" href="/export?s=%(sid)s&db=%(db)s&amp;key=%(fullkey)s" title="Export"><i class="icon-download-alt"></i></a>
    </h2>''' % ({'sid': sid, 'db': db, 'fullkey': fullkey, 'media_prefix': media_prefix})
    return out


def general_html(fullkey, sid, db, client):
    cl = client
    m_type = cl.type(fullkey)
    m_ttl = cl.ttl(fullkey)
    m_ttl = m_ttl and m_ttl or ''
    redis_version = cl.info()['redis_version']
    if redis_version >= '2.2.3':
        m_encoding = cl.object('encoding', fullkey)
    else:
        m_encoding = ''
    m_len = 0
    m_detail = ''
    m_other = ''

    if m_type == 'string':
        val = cl.get(fullkey)
        m_len = len(val)
        m_detail = string_html(fullkey, sid, db, client)
    if m_type == 'hash':
        m_len = cl.hlen(fullkey)
        m_detail = hash_html(fullkey, sid, db, client)
    elif m_type == 'list':
        m_len = cl.llen(fullkey)
        m_detail = list_html(fullkey, sid, db, client)
    elif m_type == 'set':
        m_len = len(cl.smembers(fullkey))
        m_detail = set_html(fullkey, sid, db, client)
    elif m_type == 'zset':
        m_len = len(cl.zrange(fullkey, 0, -1))
        m_detail = zset_html(fullkey, sid, db, client)

    out = '''
    <table class="table table-bordered table-striped" style="max-width: 400px">
        <tr><td><div>Type:</div></td><td><div>%(type)s</div></td></tr>
        <tr><td><div>Encoding:</div></td><td><div>%(encoding)s</div></td></tr>
        <tr><td><div>Size:</div></td><td><div>%(size)s</div></td></tr>
    </table>''' % (
        {'type': m_type, 'ttl': m_ttl, 'sid': sid, 'db': db, 'fullkey': fullkey, 'encoding': m_encoding, 'size': m_len,
         'media_prefix': media_prefix})
    return out + m_detail + m_other


def string_html(fullkey, sid, db, client):
    m_value = client.get(fullkey)
    out = '''
    <table class="table table-bordered table-striped">
        <tr><td><div>%(value)s</div></td></tr>
    </table>
    ''' % ({'value': escape(m_value)})
    return out


def hash_html(fullkey, sid, db, client):
    out = '''
    <table class="table table-bordered table-striped">
    <tr><th><div>Key</div></th><th><div>Value</div></th></tr>'''
    m_values = client.hgetall(fullkey)
    alt = False
    for key, value in m_values.items():
        if len(value) > 200:
            value = 'data(len:%s)' % len(value)
        alt_str = alt and 'class="alt"' or ''
        out += '''<tr %(alt_str)s><td><div>%(key)s</div></td><td><div>%(value)s</div></td></tr>
        ''' % ({'value': value, 'key': key,  'alt_str': alt_str})
        alt = not alt
    out += '</table>'
    return out


def list_html(fullkey, sid, db, client):
    out = '''
    <table class="table table-bordered table-striped">
    <tr><th><div>Index</div></th><th><div>Value</div></th></tr>'''
    m_values = client.lrange(fullkey, 0, -1)
    alt = False
    index = 0
    for value in m_values:
        alt_str = alt and 'class="alt"' or ''
        out += '''<tr %(alt_str)s><td><div>%(index)s</div></td><td><div>%(value)s</div></td></tr>
        ''' % ({'value': value.replace('"', '\\\''), 'index': index, 'alt_str': alt_str})
        alt = not alt
        index += 1
    out += '</table>'
    return out


def set_html(fullkey, sid, db, client):
    out = '''
    <table class="table table-bordered table-striped">
    <tr><th><div>Value</div></th></tr>'''
    m_values = client.smembers(fullkey)
    alt = False
    for value in m_values:
        alt_str = alt and 'class="alt"' or ''
        out += '''<tr %(alt_str)s><td><div>%(value)s</div></td></tr>
        ''' % (
            {'value': value, 'alt_str': alt_str})
        alt = not alt
    out += '</table>'
    return out


def zset_html(fullkey, sid, db, client):
    out = '''
    <table class="table table-bordered table-striped">
    <tr><th><div>Score</div></th><th><div>Value</div></th></tr>'''
    m_values = client.zrange(fullkey, 0, -1)
    alt = False
    for value in m_values:
        score = client.zscore(fullkey, value)
        alt_str = alt and 'class="alt"' or ''
        out += '''<tr %(alt_str)s><td><div>%(score)s</div></td><td><div>%(value)s</div></td></tr>
        ''' % ({'value': value, 'score': score, 'alt_str': alt_str})
        alt = not alt
    out += '</table>'
    return out
