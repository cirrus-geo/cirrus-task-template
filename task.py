#!/usr/bin/env python

import argparse
import json
import logging
import os
import os.path as op
import sys
from shutil import rmtree
from tempfile import mkdtemp
from boto3utils import s3

from cirruslib import Catalog, get_task_logger
from cirruslib.transfer import download_item_assets, upload_item_assets

from version import __version__

TASK_NAME='task'


def handler(payload, context={}, local=None):
    """ Handle Cirrus payload (STAC Process Catalog) """
    # get catalog
    catalog = Catalog.from_payload(payload)

    # configure logger
    logger = get_task_logger(f"{__name__}.{TASK_NAME}", catalog=catalog)

    # these are any optional parameter provided for this task
    config = catalog['process']['tasks'].get(TASK_NAME, {})
    # these are general options used when uploading output data to s3
    outopts = payload['process'].get('output_options', {})

    # validation - add specific checks on input
    # e.g., if task operates on one and only Item use this:
    assert(len(catalog['features']) == 1)
    item = catalog['features'][0]

    # create temporary work directory if not running locally
    tmpdir = mkdtemp() if local is None else local
    outpath = op.join(tmpdir, 'output')
    os.makedirs(outpath, exist_ok=True)

    try:
        # main logic - replace with own
        # download asset, e.g. a thumbnail
        item = download_item_assets(item, path=outpath, assets=['thumbnail'])

        # do something, e.g. modify asset, create new asset
        # item['assets']['asset2'] = create_new_asset(item)

        # upload new assets
        if local is not None:
            item = upload_item_assets(item, assets=['asset2'], **outopts)

        # recommended to add derived_from link
        links = [l['href'] for l in item['links'] if l['rel'] == 'self']
        if len(links) == 1:
            # add derived from link
            item ['links'].append({
                'title': 'Source STAC Item',
                'rel': 'derived_from',
                'href': links[0],
                'type': 'application/json'
            })

        catalog['features'][0] = item

    except Exception as err:
        msg = f"**task** failed: {err}"
        logger.error(msg, exc_info=True)
        raise Exception(msg)
    finally:
        # remove work directory if not running locally
        if local is None:
            logger.debug('Removing work directory %s' % tmpdir)
            rmtree(tmpdir)

    return catalog


def parse_args(args):
    """ Parse CLI arguments """
    desc = 'cirrus task'
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser0 = argparse.ArgumentParser(description=desc)

    pparser = argparse.ArgumentParser(add_help=False)
    pparser.add_argument('--version', help='Print version and exit', action='version', version=__version__)
    pparser.add_argument('--log', default=2, type=int,
                            help='0:all, 1:debug, 2:info, 3:warning, 4:error, 5:critical')
    subparsers = parser0.add_subparsers(dest='command')

    # process subcommand
    h = 'Locally process (development)'
    parser = subparsers.add_parser('local', parents=[pparser], help=h, formatter_class=dhf)
    parser.add_argument('filename', help='Full path of payload to process')
    parser.add_argument('--workdir', help='Use this as work directory', default='')

    # Cirrus process subcommand
    h = 'Process Cirrus STAC Process Catalog'
    parser = subparsers.add_parser('cirrus', parents=[pparser], help=h, formatter_class=dhf)
    parser.add_argument('url', help='s3 url to STAC Process Catalog')

    # turn Namespace into dictionary
    pargs = vars(parser0.parse_args(args))
    # only keep keys that are not None
    pargs = {k: v for k, v in pargs.items() if v is not None}

    if pargs.get('command', None) is None:
        parser.print_help()
        sys.exit(0)

    return pargs


def cli():
    args = parse_args(sys.argv[1:])
    cmd = args.pop('command')

    # logging
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=args.pop('log') * 10)
    # quiet these loud loggers
    logging.getLogger("botocore").propagate = False
    logging.getLogger("s3transfer").propagate = False
    logging.getLogger("urllib3").propagate = False

    if cmd == 'local':
        with open(args['filename']) as f:
            payload = json.loads(f.read())
        handler(payload, local=args['workdir'])
    if cmd == 'cirrus':
        # fetch input catalog
        catalog = s3().read_json(args['url'])
        catalog = handler(catalog)
        # upload return payload
        s3().upload_json(catalog, args["url"].replace('.json', '_out.json'))


if __name__ == "__main__":
    cli()