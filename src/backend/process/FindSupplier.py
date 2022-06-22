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

import re


def validate_luhn(n):
    r = [int(ch) for ch in str(n)][::-1]
    return (sum(r[0::2]) + sum(sum(divmod(d * 2, 10)) for d in r[1::2])) % 10 == 0


class FindSupplier:
    def __init__(self, ocr, log, regex, files, nb_pages, current_page, custom_page):
        self.Ocr = ocr
        self.text = ocr.header_text
        self.log = log
        self.Files = files

        self.regex = regex
        self.ocr_errors_table = ocr.ocr_errors_table
        self.found_first = True
        self.found_second = True
        self.found_third = True
        self.found_fourth = True
        self.found_fifth = True
        self.found_last_first = True
        self.found_last_second = True
        self.found_last_three = True
        self.splitted = False
        self.nbPages = nb_pages
        self.tmpNbPages = nb_pages
        self.current_page = current_page
        self.customPage = custom_page

    def search_suplier(self, column, data):
        #if data:
        #    if column.lower() in ['siret', 'siren']:
        #        if not validate_luhn(data):
        #            return False

        #    args = {
         #       'select': ['accounts_supplier.id as supplier_id', '*'],
         #       'table': ['accounts_supplier', 'addresses'],
         #       'left_join': ['accounts_supplier.address_id = addresses.id'],
         #       'where': ["TRIM(REPLACE(" + column + ", ' ', '')) = %s", 'accounts_supplier.status NOT IN (%s)'],
         #       'data': [data, 'DEL']
         #   }
         #   existing_supplier = self.Database.select(args)
         #   if existing_supplier:
         #       return existing_supplier[0]
        return False

    def process(self, regex, text_as_string, column):
        if text_as_string and not self.splitted:
            self.text = self.text.split('\n')
            self.splitted = True

        for line in self.text:
            corrected_line = ''
            for item in self.ocr_errors_table['NUMBERS']:
                pattern = r'[%s]' % self.ocr_errors_table['NUMBERS'][item]
                if text_as_string:
                    content = line
                else:
                    content = line.content

                if corrected_line:
                    content = corrected_line
                corrected_line = re.sub(pattern, item, content)

            for _data in re.finditer(r"" + regex + "", corrected_line.replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('-', '')):
                supplier = self.search_suplier(column, _data.group().replace(' ', ''))
                if supplier:
                    return supplier, line

            for _data in re.finditer(r"" + regex + "", corrected_line.replace(' ', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('-', '')):
                supplier = self.search_suplier(column, _data.group())
                if supplier:
                    return supplier, line

            for _data in re.finditer(r"" + regex + "", corrected_line.replace(' ', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '')):
                supplier = self.search_suplier(column, _data.group())
                if supplier:
                    return supplier, line
        return []

    def regenerate_ocr(self):
        self.Files.open_img(self.Files.jpg_name_header)

    def run(self, retry=False, regenerate_ocr=False, target=None, text_as_string=False):
        supplier = self.process(self.regex['VATNumberRegex'], text_as_string, 'vat_number')
        if supplier:
            self.regenerate_ocr()
            self.log.info('Supplier found : ' + supplier[0]['name'] + ' using VAT Number : ' + supplier[0]['vat_number'])
            line = supplier[1]
            if text_as_string:
                position = (('', ''), ('', ''))
            else:
                position = self.Files.return_position_with_ratio(line, target)
            data = [supplier[0]['vat_number'], position, supplier[0], self.current_page, 'vat_number']
            return data

        supplier = self.process(self.regex['SIRETRegex'], text_as_string, 'siret')
        if supplier:
            self.regenerate_ocr()
            self.log.info('Supplier found : ' + supplier[0]['name'] + ' using SIRET : ' + supplier[0]['siret'])
            line = supplier[1]
            if text_as_string:
                position = (('', ''), ('', ''))
            else:
                position = self.Files.return_position_with_ratio(line, target)
            data = [supplier[0]['vat_number'], position, supplier[0], self.current_page, 'siret']
            return data

        supplier = self.process(self.regex['SIRENRegex'], text_as_string, 'siren')
        if supplier:
            self.regenerate_ocr()
            self.log.info('Supplier found : ' + supplier[0]['name'] + ' using SIREN : ' + supplier[0]['siren'])
            line = supplier[1]
            if text_as_string:
                position = (('', ''), ('', ''))
            else:
                position = self.Files.return_position_with_ratio(line, target)
            data = [supplier[0]['vat_number'], position, supplier[0], self.current_page, 'siren']
            return data

        supplier = self.process(self.regex['IBANRegex'], text_as_string, 'iban')
        if supplier:
            self.regenerate_ocr()
            self.log.info('Supplier found : ' + supplier[0]['name'] + ' using IBAN : ' + supplier[0]['iban'])
            line = supplier[1]
            if text_as_string:
                position = (('', ''), ('', ''))
            else:
                position = self.Files.return_position_with_ratio(line, target)
            data = [supplier[0]['vat_number'], position, supplier[0], self.current_page, 'iban']
            return data
        else:
            if not retry:
                self.found_first = False
            elif retry and self.found_second:
                self.found_second = False
            elif retry and not self.found_second and self.found_third:
                self.found_third = False
            elif retry and not self.found_third and self.found_fourth:
                self.found_fourth = False
            elif retry and not self.found_fourth and self.found_fifth:
                self.found_fifth = False
            elif retry and not self.found_fifth and self.found_last_first:
                if self.tmpNbPages == 1:
                    return False
                self.found_last_first = False
            elif retry and not self.found_last_first and self.found_last_second:
                self.found_last_second = False
            elif retry and not self.found_last_second and self.found_last_three:
                self.found_last_three = False

            # If we had to change footer to header
            # Regenerator OCR with the full image content
            if regenerate_ocr:
                self.regenerate_ocr()
                return False  # Return False because if we reach this, all the possible tests are done. Mandatory to avoid infinite loop

        if self.customPage:
            self.log.info('No supplier informations found in the first and last page. Try last page - 1')
            file = self.Files.custom_file_name
            image = self.Files.open_image_return(file)
            self.text = self.Ocr.line_box_builder(image)
            return self.run(retry=True, regenerate_ocr=True, target='footer')

        # If NO supplier identification are found in the header (default behavior),
        # First apply image correction
        if not retry and not self.found_first:
            self.log.info('No supplier informations found in the header, improve image and retry...')
            improved_image = self.Files.improve_image_detection(self.Files.jpg_name_header)
            self.Files.open_img(improved_image)
            self.text = self.Ocr.line_box_builder(self.Files.img)
            return self.run(retry=True, target=None)

        # If, even with improved image, nothing was found, check the footer
        if retry and not self.found_second and self.found_third:
            self.log.info('No supplier informations found with improved image, try with footer...')
            self.text = self.Ocr.footer_text
            return self.run(retry=True, target='footer')

        # If NO supplier identification are found in the footer,
        # Apply image improvment
        if retry and not self.found_third and self.found_fourth:
            self.log.info('No supplier informations found in the footer, improve image and retry...')
            improved_image = self.Files.improve_image_detection(self.Files.jpg_name_footer)
            self.Files.open_img(improved_image)
            self.text = self.Ocr.line_box_builder(self.Files.img)
            return self.run(retry=True, target='footer')

        # If NO supplier identification are found in the improved footer,
        # Try using another tesseract function to extract text on the header
        if retry and not self.found_fourth and self.found_fifth:
            self.log.info('No supplier informations found in the footer, change Tesseract function to retrieve text and retry on header...')
            improved_image = self.Files.improve_image_detection(self.Files.jpg_name_header)
            self.Files.open_img(improved_image)
            self.text = self.Ocr.text_builder(self.Files.img)
            return self.run(retry=True, target='header', text_as_string=True)

        if retry and not self.found_fifth and self.found_last_first:
            self.splitted = False
            self.log.info('No supplier informations found in the header as string, change Tesseract function to retrieve text and retry on footer...')
            improved_image = self.Files.improve_image_detection(self.Files.jpg_name_footer)
            self.Files.open_img(improved_image)
            self.text = self.Ocr.text_builder(self.Files.img)
            self.current_page = 1
            return self.run(retry=True, target='footer', text_as_string=True)

        # Try now with the last page
        if retry and not self.found_last_first and self.found_last_second:
            self.log.info('No supplier informations found in the first page, try with the last page header')
            self.text = self.Ocr.header_last_text
            self.current_page = self.nbPages  # Use the last page number because we search on the last page
            return self.run(retry=True, target='header')

        if retry and not self.found_last_second and self.found_last_three:
            self.log.info('No supplier informations found in the header last page, try with the improved last page header')
            improved_image = self.Files.improve_image_detection(self.Files.jpg_name_last_header)
            self.Files.open_img(improved_image)
            self.text = self.Ocr.line_box_builder(self.Files.img)
            self.current_page = self.nbPages
            return self.run(retry=True, target='header')

        if retry and not self.found_last_three:
            self.log.info('No supplier informations found in the header last page, try with the footer last page header')
            self.text = self.Ocr.footer_last_text
            self.current_page = self.nbPages
            return self.run(retry=True, regenerate_ocr=True, target='footer')

        self.log.info('No supplier found...')
        return False
