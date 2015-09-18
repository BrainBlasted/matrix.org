#! /usr/bin/env python

import sys

def import_error(module, package, debian, error):
    sys.stderr.write((
        "Error importing %(module)s: %(error)r\n"
        "To install %(module)s run:\n"
        "  pip install %(package)s\n"
        "or on Debian run:\n"
        "  sudo apt-get install python-%(debian)s\n"
    ) % locals())
    if __name__=='__main__':
        sys.exit(1)

try:
    import jsonschema
except ImportError as e:
    import_error("jsonschema", "jsonschema", "jsonschema", e)
    raise

try:
    import yaml
except ImportError as e:
    import_error("yaml", "PyYAML", "yaml", e)
    raise

import json
import os

def check_response(filepath, request, code, response):
    try:
        example = json.loads(
            response.get('examples', {}).get('application/json', "null")
        )
    except Exception as e:
        raise ValueError("Error parsing JSON example response for %r %r" % (
            request, code
        ), e)
    schema = response.get('schema')
    fileurl = "file://" + os.path.abspath(filepath)
    if example and schema:
        try:
            print ("Checking schema for: %r %r %r" % (filepath, request, code))
            # Setting the 'id' tells jsonschema where the file is so that it
            # can correctly resolve relative $ref references in the schema
            schema['id'] = fileurl
            jsonschema.validate(example, schema)
        except Exception as e:
            raise ValueError("Error validating JSON schema for %r %r" %(
                request, code
            ), e)


def check_swagger_file(filepath):
    with open(filepath) as f:
        swagger = yaml.load(f)

    for path, path_api in swagger['paths'].items():
        for method, request_api in path_api.items():
            request = "%s %s" % (method.upper(), path)
            try:
                responses = request_api['responses']
            except KeyError:
                raise ValueError("No responses for %r" % (request,))
            for code, response in responses.items():
                check_response(filepath, request, code, response)


if __name__=='__main__':
    for path in sys.argv[1:]:
        try:
            check_swagger_file(path)
        except Exception as e:
            raise ValueError("Error checking file %r" % (path,), e)
