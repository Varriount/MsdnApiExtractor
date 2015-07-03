import codecs
import warnings
from scrapy.contrib.exporter import BaseItemExporter
import re
import os

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
uni = lambda x: unicode(x)


def iterlines(string):
    return iter(string.splitlines())


def extract_filename(string):
    value = re.match(u'(.+?)\.(?:dll|h|lib)', string)
    if value is not None:
        value = uni(value.group(1))
    return (value or '')


def uopen(file, mode='r', buffering=-1, encoding=None,
          errors=None, newline=None, closefd=True, opener=None):
    if newline is not None:
        warnings.warn('newline is not supported in py2')
    if not closefd:
        warnings.warn('closefd is not supported in py2')
    if opener is not None:
        warnings.warn('opener is not supported in py2')
    return codecs.open(filename=file, mode=mode, encoding=encoding,
                       errors=errors, buffering=buffering)


def serialize_metadata(metadata):
    pre_result = ['// Metadata:']
    for key, value in metadata.items():
        pre_result.append(
            u'//   {0}: {1}'.format(
                uni(key.capitalize()),
                uni(value)
            )
        )
    return pre_result


enum_entry_matcher = u'(\w+)\s+((?:0x[0-9a-fA-F]+)|\d+)\s*(.*)'
enum_start_line = u'typedef enum EnumType{0} {{ // {1}'.format
enum_value_line = u'  {0} = {1},'.format
enum_end_line = u'};'


def serialize_tables(tables):
    if len(tables) == 0:
        return ''
    other_entries = [u'// Tables:']
    enum_entries = []
    enum_count = 1
    for header, table in tables:
        # Case 1 - It's an enum
        entry_lines = [enum_start_line(enum_count, uni(header))]
        for entry in table:
            match = re.match(enum_entry_matcher, entry)
            if match is None:
                break
            line = enum_value_line(
                uni(match.group(1)),
                uni(match.group(2))
            )
            if match.group(3):
                line += u' // {0}'.format(uni(match.group(3)))
            entry_lines.append(line)
        else:
            enum_entries.extend(entry_lines)
            enum_entries.append(enum_end_line)
            enum_count += 1
            continue

        # Case 2 - Not an enum
        other_entries.append(u'//   {0}'.format(uni(header)))
        for entry in table:
            other_entries.append(u"//     '{0}',".format(uni(entry)))

    if len(other_entries) == 1:
        return enum_entries
    other_entries.extend(enum_entries)
    return other_entries


class ApiExporter(BaseItemExporter):

    def __init__(self, file_handle, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file_handle

    def export_item(self, item):
        pre_result = []
        pre_result.extend(serialize_tables(item['tables']))
        pre_result.append(item['code'])
        pre_result.append(u'//')
        pre_result.append(u'// URL: {0}'.format(item['url']))
        pre_result.extend(serialize_metadata(item['metadata']))
        pre_result.append("\n\n")
        contents = u'\n'.join(pre_result).replace(u'\x00', u'').encode('utf-8')

        old_position = file.tell()
        self.file.write(contents)
        self.file.flush()
        os.fsync(self.file.fileno()),
        assert(old_position + len(contents) == file.tell())


class ApiExporterDict(dict):

    def __missing__(self, key):
        value = ApiExporter(open(key, 'w'))
        self[key] = value
        return value


class ApiExportPipeline(object):

    def __init__(self):
        self.links_log = open('crawled_links.txt', 'w')
        self.exporters = ApiExporterDict()
        self.spiders = 0

    def open_spider(self, spider):
        self.spiders += 1

    def close_spider(self, spider):
        self.spiders -= 1
        if self.spiders == 0:
            for exporter in self.exporters.items():
                exporter.file.close()

    def process_item(self, item, spider):
        is_empty = (
            len(item['code']) == 0 and
            len(item['metadata']) == 0 and
            len(item['tables']) == 0
        )

        if is_empty:
            log_line = "Empty URL: '{0}'\n".format(item['url'])
        else:
            log_line = "Non-Empty URL: '{0}'\n".format(item['url'])
            get_metadata = item['metadata'].get
            file_name = (
                get_metadata('header') or
                get_metadata('dll') or
                get_metadata('library') or
                ''
            )
            file_name = extract_filename(file_name) or 'other'
            file_name += '.txt'

            exporter = self.exporters[file_name]
            exporter.export_item(item)

        self.links_log.write(log_line.replace('\x00', '').encode("utf-8"))
        return item
