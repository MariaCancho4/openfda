"""
OPENFDA FINAL PROJECT

It covers the whole project with all the extensions.
"""

import http.server
import json
import socketserver
import http.client

socketserver.TCPServer.allow_reuse_address = True

PORT = 8000
IP = '127.0.0.1'

# EXTENSION III: include the logic to communicate with the OpenFDA remote API.
class OpenFDAClient():

    def set_arguments(self, params):
        headers = {'User-Agent': 'http-client'}

        con = http.client.HTTPSConnection("api.fda.gov")

        query_url = "/drug/label.json"
        if params:
            query_url += "?" + params

        print("fetching", query_url)

        con.request("GET", query_url, None, headers)
        
        response = con.getresponse()
        print("Status:", response.status, response.reason)
        data = response.read().decode("utf-8")
        con.close()

        result = json.loads(data)
        return result['results'] if 'results' in result else []
            
        

        

    def search_drugs(self, active_ingredient, limit=10):

        params = 'search=active_ingredient:"{}"'.format(active_ingredient)
        
        if limit: 
            params += "&limit=" + str(limit)
        drugs = self.set_arguments(params) 
        return drugs['results'] if 'results' in drugs else []

    def search_companies_info(self, company_name, limit=10):

        params = 'search=openfda.manufacturer_name:"%s"' % company_name
        if limit:
            params += "&limit=" + str(limit)
        drugs = self.set_arguments(params)

        return drugs



    def list_drugs(self, limit=10):

        params = "limit=" + str(limit)

        drugs = self.set_arguments(params)

        return drugs

   

# EXTENSION III: includes the logic to extract the data from drugs result. 
class OpenFDAParser():


    def parse_drugs(self, drugs):

        drugs_labels = []

        for drug in drugs:
            drug_label = drug['id']
            if 'active_ingredient' in drug:
                drug_label += " " + drug['active_ingredient'][0]
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                drug_label += " " + drug['openfda']['manufacturer_name'][0]

            drugs_labels.append(drug_label)

        return drugs_labels

    def parse_companies_info(self, drugs):

        companies_info = []
        for drug in drugs:
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                companies_info.append(drug['openfda']['manufacturer_name'][0])
            else:
                companies_info.append("Unknown")

            companies_info.append(drug['id'])

        return companies_info

    # EXTENSION I: list warnings
    def parse_warnings(self, drugs):

        warnings = []

        for drug in drugs:
            if 'warnings' in drug and drug['warnings']:
                warnings.append(drug['warnings'][0])
            else:
                warnings.append("Unknown")
        return warnings


# EXTENSION III: includes the logic to the HTML visualization.
class OpenFDAHTML():

    def build_html_list(self, result):

        html_list = "<ul>"
        for item in result:
            html_list += "<li>" + item + "</li>"
        html_list += "</ul>"

        return html_list

    # EXTENSION II: 404 PAGE
    def show_page_not_found(self):
        with open("page_not_found.html") as html_file:
            return html_file.read()

        

# Refactored HTTPRequestHandler class
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    # Handle all the GET Requests
    def do_GET(self):

        # initialize the classes objects
        client = OpenFDAClient()
        html_builder = OpenFDAHTML()
        json_parser = OpenFDAParser()

        response_code = 404
        response = html_builder.show_page_not_found()

        if self.path == "/":
            # Return home page
            with open("index.html") as f:
                response = f.read()        
        
        if 'searchDrug' in self.path:
            active_ingredient = None
            limit = 10
            params = self.path.split("?")[1].split("&")
            for param in params:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                if param_name == 'active_ingredient':
                    active_ingredient = param_value
                elif param_name == 'limit':
                    limit = param_value
            result = client.search_drugs(active_ingredient, limit)
            response = html_builder.build_html_list(json_parser.parse_drugs(result))
        
        elif 'listDrugs' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            result = client.list_drugs(limit)
            response = html_builder.build_html_list(json_parser.parse_drugs(result))
        
        elif 'searchCompany' in self.path:
            company_name = None
            limit = 10
            params = self.path.split("?")[1].split("&")
            for param in params:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                if param_name == 'company':
                    company_name = param_value
                elif param_name == 'limit':
                    limit = param_value
            result = client.search_companies_info(company_name, limit)
            response = html_builder.build_html_list(json_parser.parse_companies_info(result))

        elif 'listCompanies' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            result = client.list_drugs(limit)
            response = html_builder.build_html_list(json_parser.parse_companies_info(result))

        # EXTENSION I: List Warnings
        elif 'listWarnings' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            result = client.list_drugs(limit)
            response = html_builder.build_html_list(json_parser.parse_warnings(result))
        
        
        # Extension IV: Redirect and Authentication
        if 'secret' in self.path:
            response_code = 401
            self.send_header('WWW-Authenticate', ' WWW-Authenticate de basic Realm')
        elif 'redirect' in self.path:
            response_code = 302
            self.send_header('Location', 'http://localhost:8000/')

        # Send response status code
        self.send_response(response_code)

        # Send generic headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # show html response
        self.wfile.write(bytes(response, "utf8"))


Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()