import requests

from erdpy import errors


def do_get(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        parsed = response.json()
        return parsed
    except requests.HTTPError as err:
        error_data = _extract_error_from_response(err.response)
        raise errors.BlockAtlasRequestError(url, error_data)
    except requests.ConnectionError as err:
        raise errors.BlockAtlasRequestError(url, err)
    except Exception as err:
        raise errors.BlockAtlasRequestError(url, err)


def do_post(url, payload):
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        parsed = response.json()
        return parsed
    except requests.HTTPError as err:
        error_data = _extract_error_from_response(err.response)
        raise errors.BlockAtlasRequestError(url, error_data)
    except requests.ConnectionError as err:
        raise errors.BlockAtlasRequestError(url, err)
    except Exception as err:
        raise errors.BlockAtlasRequestError(url, err)


def _extract_error_from_response(response):
    try:
        return response.json()
    except Exception:
        return response.text
