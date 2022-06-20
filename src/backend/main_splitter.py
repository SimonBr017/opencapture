# This file is part of Open-Capture for Invoices.

# Open-Capture for Invoices is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Open-Capture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Open-Capture for Invoices. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.

# @dev : Nathan Cheval <nathan.cheval@outlook.fr>

import os
import sys
import time
import json
import tempfile
from kuyruk import Kuyruk
from src.backend.main import timer, check_file, create_classes
from src.backend.import_classes import _Files, _Config, _Splitter, _SeparatorQR, _Log

OCforInvoices = Kuyruk()


@OCforInvoices.task(queue='splitter')
def launch(args):
    start = time.time()

    # Init all the necessary classes
    config_name = _Config(args['config'])
    config_file = config_name.cfg['PROFILE']['cfgpath'] + '/config_' + config_name.cfg['PROFILE']['id'] + '.ini'

    if not os.path.exists(config_file):
        sys.exit('Config file couldn\'t be found')

    config, regex, log, _, database, _, smtp, docservers, configurations = create_classes(config_file)
    tmp_folder = tempfile.mkdtemp(dir=docservers['SPLITTER_BATCHES']) + '/'
    filename = tempfile.NamedTemporaryFile(dir=tmp_folder).name
    files = _Files(filename, log, docservers, configurations, regex)

    remove_blank_pages = False
    if 'input_id' in args:
        input_settings = database.select({
            'select': ['*'],
            'table': ['inputs'],
            'where': ['input_id = %s', 'module = %s'],
            'data': [args['input_id'], 'splitter'],
        })
        if input_settings:
            remove_blank_pages = input_settings[0]['remove_blank_pages']

    separator_qr = _SeparatorQR(log, config, tmp_folder, 'splitter', files, remove_blank_pages, docservers)
    splitter = _Splitter(config, database, separator_qr, log, docservers)

    if args.get('isMail') is not None and args['isMail'] is True:
        log = _Log((args['log']), smtp)
        log.info('Process attachment n°' + args['cpt'] + '/' + args['nb_of_attachments'])

    database.connect()
    if args['file'] is not None:
        path = args['file']
        if check_file(files, path, log, docservers) is not False:
            if 'input_id' in args and args['input_id']:
                splitter_method = database.select({
                    'select': ['splitter_method_id'],
                    'table': ['inputs'],
                    'where': ['status <> %s', 'input_id = %s', 'module = %s'],
                    'data': ['DEL', args['input_id'], 'splitter']
                })[0]
                available_split_methods_path = docservers['SPLITTER_METHODS_PATH'] + "/splitter_methods.json"
                if len(splitter_method) > 0 and os.path.isfile(available_split_methods_path):
                    with open(available_split_methods_path, encoding='UTF-8') as json_file:
                        available_split_methods = json.load(json_file)
                        for available_split_method in available_split_methods['methods']:
                            if available_split_method['id'] == splitter_method['splitter_method_id']:
                                split_method = _Splitter.import_method_from_script(docservers['SPLITTER_METHODS_PATH'],
                                                                                   available_split_method['script'],
                                                                                   available_split_method['method'])
                                log.info('Split using method : {}'.format(available_split_method['id']))
                                split_method(args, path, log, splitter, files, tmp_folder, config, docservers)
            else:
                log.error("The input_id doesn't exists in database")
    database.conn.close()
    end = time.time()
    log.info('Process end after ' + timer(start, end) + '')
