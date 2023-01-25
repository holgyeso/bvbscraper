import requests
import re
from bs4 import BeautifulSoup


def get_url_response(url: str, headers: dict = None) -> requests.Response:
    """
    Returns the response of a GET request to the specified URL if it successful.
    :param url: the URL from that information must be retrieved
    :type url: str
    :param headers: special header definition
    :type headers: dict
    :return: the Response object if the request was successful
    :rtype: requests.models.Response object
    :raises ValueError: in case the response is not valid (contains no text or the response code was not 200)
    """

    response = requests.get(url, headers=headers)

    if response.status_code != 200 and response.text == '':
        raise ValueError("Response is not valid.")
    return response


def post_request(url: str, data_dict: dict, headers: dict = None) -> requests.Response:
    """
    Returns the response of a POST request to the specified URL if it successful.
    :param url: the URL from that information must be retrieved
    :type url: str
    :param data_dict: the payload of the POST request
    :type data_dict: dict
    :param headers: special header definition
    :type headers: dict
    :return: the Response object if the request was successful
    :rtype: requests.models.Response object
    :raises ValueError: in case the response is not valid (contains no text or the response code was not 200)
    """
    response = requests.post(url, data=data_dict, headers=headers)
    if response.status_code != 200 and response.text == '':
        raise ValueError("Response is not valid.")
    return response


def post_response_instrument_details_form(symbol: str, button: str, form_id: str = None) -> str:
    """
    The function is primarily used to scrape information from BVB's FinancialInstrumentsDetails.aspx site.

    The switch among the "Overview", "Trading", "Charts", "News", "Financials", "Issuer profile" buttons is
    implemented using forms in ASP.NET with POST requests. The form contains some hidden fields (e.g. __LASTFOCUS,
    __EVENTTARGET) that are sent in the POST request for validation.

    The function imitates how a user would interact with the page: first the "Overview" page is loaded, and then the
    user would click on one button to retrieve another page. The HTML content of that page is returned back.

    :param symbol: the symbol that's information must be retrieved
    :type symbol: str
    :param button: The exact name of the button that the user would click on in the UI. Possible values: "Overview",
    "Trading", "Charts", "News", "Financials", "Issuer profile".
    :type button: str
    :param form_id: The HTML id of the form element that make POST request in the background. If there are multiple
     forms with the same id or no id is given, the first element with form tag (with the given id) will be considered.
     The id attribute of the form can be inspected with the browser's Inspector.
    :type form_id: str
    :return: HTML content of the page that would be retrieved when the user would click on the button provided in
    button parameter.
    :rtype: text (HTML content)
    :raises TypeError: when the button parameter is not of type str.
    :raises ValueError:
    + when the provided button value is not a valid one
    + when there is no form element or form element with specified id in the provided url
    + when the button has no name property
    """
    _BASE_URL = "https://www.bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s="

    possible_buttons = ['OVERVIEW', 'TRADING', 'CHARTS', 'NEWS', 'FINANCIALS', 'ISSUER PROFILE']
    default_button = 'OVERVIEW'  # when the page loads, the default_button is selected.

    url = _BASE_URL + symbol

    # validate symbol
    if type(symbol) != str:
        raise TypeError("The symbol must be of type str.")
    else:
        symbol = symbol.upper()
        if not re.findall(r"^[A-Z0-9]+$", symbol):
            raise ValueError(f"Invalid symbol format {symbol}.")

    # validate button parameter

    if type(button) != str:
        raise TypeError("The button must be of type str.")

    button = button.upper()

    if button not in possible_buttons:
        raise ValueError("Invalid button.")

    # retrieve the default page with GET
    get_response = get_url_response(url=url).content

    if default_button == 'Overview':
        return get_response

    # initialize a BeautifulSoup4 instance on the base site, got with GET request.
    soup = BeautifulSoup(get_response, 'html.parser')

    # select only the form element from html
    form = ""
    if form_id is None:
        form = soup.find('form')
    else:
        form = soup.find('form', id=form_id)  # form element with id. If id=None, it won't find only form element

    if form is None:
        raise ValueError("There is no form element in the given HTML.")  # TODO: revise error type

    # construct the POST request's payload

    post_data = {
        "ctl00$body$ctl02$NewsBySymbolControl$chOutVolatility": "on",
        "ctl00$body$ctl02$NewsBySymbolControl$chOutInsiders": "on"
    }

    # extract hidden fields that begin with __
    for inp in form.find_all('input', type="hidden"):
        if inp.get('name') and inp.get('name').startswith("__"):  # if the name attribute of input exists
            post_data[inp.get('name')] = inp.get('value')

    # extract the button that 'would be pressed' on UI to retrieve the information
    for btn in form.find_all('input', type='submit'):
        if btn.get("value").upper() == button:
            handler = btn.get("name")
            if handler is None:
                raise ValueError("The target button does not have name property")  # TODO: revise error type
            post_data["ctl00$MasterScriptManager"] = 'ctl00$body$updIfttc|' + handler
            post_data[handler] = btn.get("value")
            break

    headers = {'Referer': url}

    return post_request(url, data_dict=post_data, headers=headers).text
