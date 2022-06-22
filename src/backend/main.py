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
import json
import os
import sys
import time
import tempfile
from kuyruk import Kuyruk
from flask import current_app
from .functions import recursive_delete, get_custom_array
from .import_classes import  _PyTesseract, _Files, _Log, _Config, _SeparatorQR, _Spreadsheet, _SMTP, _Mail

custom_array = get_custom_array()

if 'OCForInvoices' not in custom_array:
    from src.backend.process import OCForInvoices as OCForInvoices_process
else:
    OCForInvoices_process = getattr(__import__(custom_array['OCForInvoices']['path'],
                                               fromlist=[custom_array['OCForInvoices']['module']]),
                                    custom_array['OCForInvoices']['module'])


def create_classes_from_current_config():
    config_name = _Config(current_app.config['CONFIG_FILE'])
    config_file = current_app.config['CONFIG_FOLDER'] + '/config_' + config_name.cfg['PROFILE']['id'] + '.ini'
    config = _Config(current_app.config['CONFIG_FOLDER'] + '/config_' + config_name.cfg['PROFILE']['id'] + '.ini')
    config_mail = _Config(config.cfg['GLOBAL']['configmail'])
    smtp = _SMTP(
        config_mail.cfg['GLOBAL']['smtp_notif_on_error'],
        config_mail.cfg['GLOBAL']['smtp_host'],
        config_mail.cfg['GLOBAL']['smtp_port'],
        config_mail.cfg['GLOBAL']['smtp_login'],
        config_mail.cfg['GLOBAL']['smtp_pwd'],
        config_mail.cfg['GLOBAL']['smtp_ssl'],
        config_mail.cfg['GLOBAL']['smtp_starttls'],
        config_mail.cfg['GLOBAL']['smtp_dest_admin_mail'],
        config_mail.cfg['GLOBAL']['smtp_delay'],
        config_mail.cfg['GLOBAL']['smtp_auth'],
        config_mail.cfg['GLOBAL']['smtp_from_mail'],
    )
    log = _Log(config.cfg['GLOBAL']['logfile'], smtp)


    regex = {}
    docservers = {}
    configurations = {}

    #_ds = database.select({
    #    'select': ['*'],
    #    'table': ['docservers'],
    #})
    #for _d in _ds:
    #    docservers[_d['docserver_id']] = _d['path']

    #_config = database.select({
    #    'select': ['*'],
    #    'table': ['configurations'],
    #})

    #for _c in _config:
    #    configurations[_c['label']] = _c['data']['value']

    #_regex = database.select({
    #    'select': ['regex_id', 'content'],
    #    'table': ['regex'],
    #    'where': ['lang = %s'],
    #    'data': [configurations['locale']],
    #})

    #for _r in _regex:
    #    regex[_r['regex_id']] = _r['content']
    file_docservers = open("instance/config/docservers.json", "r")
    docservers = json.load(file_docservers)
    
    file_configurations = open("instance/config/configuration.json", 'r')
    configurations = json.load(file_configurations)

    spreadsheet = _Spreadsheet(log, docservers, config)
    ocr = _PyTesseract(configurations['locale'], log, config, docservers)
    file_regex = open("instance/config/regex.json", "r")
    regex = json.load(file_regex)


    spreadsheet = _Spreadsheet(log, docservers, config)
    filename = docservers['TMP_PATH'] + '/tmp/'
    files = _Files(filename, log, docservers, configurations, regex)
    ocr = _PyTesseract(configurations['locale'], log, config, docservers)

    return config, regex, files, ocr, log, config_file, spreadsheet, smtp, docservers, configurations


def create_classes(config_file):
    config = _Config(config_file)
    config_mail = _Config(config.cfg['GLOBAL']['configmail'])
    smtp = _SMTP(
        config_mail.cfg['GLOBAL']['smtp_notif_on_error'],
        config_mail.cfg['GLOBAL']['smtp_host'],
        config_mail.cfg['GLOBAL']['smtp_port'],
        config_mail.cfg['GLOBAL']['smtp_login'],
        config_mail.cfg['GLOBAL']['smtp_pwd'],
        config_mail.cfg['GLOBAL']['smtp_ssl'],
        config_mail.cfg['GLOBAL']['smtp_starttls'],
        config_mail.cfg['GLOBAL']['smtp_dest_admin_mail'],
        config_mail.cfg['GLOBAL']['smtp_delay'],
        config_mail.cfg['GLOBAL']['smtp_auth'],
        config_mail.cfg['GLOBAL']['smtp_from_mail'],
    )
    log = _Log(config.cfg['GLOBAL']['logfile'], smtp)


    regex = {}
    docservers = {}
    configurations = {}

    #_ds = database.select({
    #    'select': ['*'],
    #    'table': ['docservers'],
    #})
    #for _d in _ds:
    #    docservers[_d['docserver_id']] = _d['path']

    #_config = database.select({
    #    'select': ['*'],
    #    'table': ['configurations'],
    #})

    #for _c in _config:
    #    configurations[_c['label']] = _c['data']['value']

    #_regex = database.select({
    #    'select': ['regex_id', 'content'],
    #    'table': ['regex'],
    #    'where': ['lang = %s'],
    #    'data': [configurations['locale']],
    #})

    #for _r in _regex:
    #    regex[_r['regex_id']] = _r['content']
    file_docservers = open("instance/config/docservers.json", "r")
    docservers = json.load(file_docservers)
    
    file_configurations = open("instance/config/configuration.json", 'r')
    configurations = json.load(file_configurations)

    spreadsheet = _Spreadsheet(log, docservers, config)
    ocr = _PyTesseract(configurations['locale'], log, config, docservers)
    file_regex = open("instance/config/regex.json", "r")
    regex = json.load(file_regex)

    #tfconfiguration = open("configuration.json", "w")
    #json.dump(configurations, tfconfiguration)
    #tfconfiguration.close()

    #tfdocservers = open("docservers.json", "w")
    #json.dump(docservers, tfdocservers)
    #tfdocservers.close()


    return config, regex, log, ocr, spreadsheet, smtp, docservers, configurations


def check_file(files, path, log, docservers):
    if not files.check_file_integrity(path, docservers):
        log.error('The integrity of file could\'nt be verified : ' + str(path))
        return False
    return True


def timer(start_time, end_time):
    hours, rem = divmod(end_time - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)


# def get_typo(config, path, log):
#     invoice_classification.MODEL_PATH = config.cfg['AI-CLASSIFICATION']['modelpath']
#     invoice_classification.PREDICT_IMAGES_PATH = config.cfg['AI-CLASSIFICATION']['trainimagepath']
#     invoice_classification.TRAIN_IMAGES_PATH = config.cfg['AI-CLASSIFICATION']['predictimagepath']
#     typo, confidence = invoice_classification.predict_typo(path)
#
#     if typo:
#         if confidence >= config.cfg['AI-CLASSIFICATION']['confidencemin']:
#             log.info('Typology n°' + typo + ' found using AI with a confidence of ' + confidence + '%')
#             return typo
#         else:
#             log.info('Typology can\'t be found using AI, the confidence is too low :'
#                      ' Typo n°' + typo + ', confidence : ' + confidence + '%')
#             return False
#     else:
#         log.info('Typology can\'t be found using AI')
#         return False


def str2bool(value):
    """
    Function to convert string to boolean

    :return: Boolean
    """
    return value.lower() in "true"


OCforInvoices_worker = Kuyruk()


@OCforInvoices_worker.task(queue='invoices')
def launch(args):
    start = time.time()

    # Init all the necessary classes
    config_name = _Config(args['config'])
    config_file = config_name.cfg['PROFILE']['cfgpath'] + '/config_' + config_name.cfg['PROFILE']['id'] + '.ini'

    if not os.path.exists(config_file):
        sys.exit('config file couldn\'t be found')

    config, regex, log, ocr, _, smtp, docservers, configurations = create_classes(config_file)
    tmp_folder = tempfile.mkdtemp(dir=docservers['TMP_PATH'])
    filename = tempfile.NamedTemporaryFile(dir=tmp_folder).name
    files = _Files(filename, log, docservers, configurations, regex)

    #if 'languages' in args:
     #   languages = args['languages']
    #else:
    languages = {
    "fr": {
        "label" : "Francais",
        "lang_code": "fra",
        "moment_lang_code": "fr-FR",
        "date_format": "%d %m %Y"
    },
    "en": {
        "label" : "English",
        "lang_code": "eng",
        "moment_lang_code": "en-GB",
        "date_format": "%m %d %Y"
    }
}

    remove_blank_pages = False
    splitter_method = False
    #if 'input_id' in args:
    #    input_settings = database.select({
    #        'select': ['*'],
    #        'table': ['inputs'],
    #        'where': ['input_id = %s', 'module = %s'],
    #        'data': [args['input_id'], 'verifier'],
    #    })
    #    if input_settings:
    #        splitter_method = input_settings[0]['splitter_method_id']
    #        remove_blank_pages = input_settings[0]['remove_blank_pages']

    separator_qr = _SeparatorQR(log, config, tmp_folder, 'verifier', files, remove_blank_pages, docservers)
    mail_class = None

    if args.get('isMail') is not None and args['isMail'] is True:
        config_mail = _Config(args['config_mail'])
        mail_class = _Mail(
            config_mail.cfg[args['process']]['host'],
            config_mail.cfg[args['process']]['port'],
            config_mail.cfg[args['process']]['login'],
            config_mail.cfg[args['process']]['password']
        )
        log = _Log((args['log']), smtp)
        log.info('Process attachment n°' + args['cpt'] + '/' + args['nb_of_attachments'])

    if args.get('isMail') is None or args.get('isMail') is False:
        if splitter_method and splitter_method == 'qr_code_OC':
            separator_qr.enabled = True

    #database.connect()

    # Start process
    try:
        with open('datas.json'):
            log.info("datas.json found")
            os.remove("datas.json")
    except IOError:
        log.info("datas.json not found")
    if 'file' in args and args['file'] is not None:
        path = args['file']
        log.filename = os.path.basename(path)
        if separator_qr.enabled:
            if check_file(files, path, log, docservers) is not False:
                separator_qr.run(path)
            path = separator_qr.output_dir_pdfa if str2bool(separator_qr.convert_to_pdfa) is True else separator_qr.output_dir

            for file in os.listdir(path):
                # if config.cfg['AI-CLASSIFICATION']['enabled'] == 'True':
                #     typo = get_typo(config, path + file, log)

                if check_file(files, path + file, log, docservers) is not False:
                    res = OCForInvoices_process.process(args, path + file, log, config, files, ocr, regex, docservers, configurations, languages)
                    if not res:
                        mail_class.move_batch_to_error(args['batch_path'], args['error_path'], smtp, args['process'], args['msg'], config, docservers)
                        log.error('Error while processing e-mail', False)
        elif splitter_method == 'separate_by_document':
            list_of_files = separator_qr.split_document_every_two_pages(path)
            for file in list_of_files:
                # if config.cfg['AI-CLASSIFICATION']['enabled'] == 'True':
                #     typo = get_typo(config, file, log)

                if check_file(files, file, log, docservers) is not False:
                    res = OCForInvoices_process.process(args, file, log, config, files, ocr, regex, docservers, configurations, languages)
                    if not res:
                        mail_class.move_batch_to_error(args['batch_path'], args['error_path'], smtp, args['process'], args['msg'], config, docservers)
                        log.error('Error while processing e-mail', False)
            os.remove(path)
        else:
            # if config.cfg['AI-CLASSIFICATION']['enabled'] == 'True':
            #     typo = get_typo(config, path, log)

            if check_file(files, path, log, docservers) is not False:
                res = OCForInvoices_process.process(args, path, log, config, files, ocr, regex, docservers, configurations, languages)
                if not res:
                    mail_class.move_batch_to_error(args['batch_path'], args['error_path'], smtp, args['process'], args['msg'], config, docservers)
                    log.error('Error while processing e-mail', False)

    recursive_delete(tmp_folder, log)
    #database.conn.close()
    end = time.time()
    log.info('Process end after ' + timer(start, end) + '')
    
    
    tf = open("datas.json", "r")
    datas = json.load(tf)
    log.info(datas)
    print(datas)

