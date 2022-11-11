# Copyright (c) Sarus Systems Systems Limited 2022  

import sys
import json

from pprint import pprint

modules_required = []

try:
    import requests as r
except:
    modules_required.append('requests')
    print("Module 'requests' not found.")


try:
    import colorama
    from colorama import Fore, Style
    colorama.init(strip=False)
    use_colour_text = True
except:
    use_colour_text = False
    print("Module 'colorama' not found.")

try:
    from typing import Any, Optional
except:
    modules_required.append('typing')
    print("Module 'typing' not found.")



if modules_required:
    text = "[WARNING] Following required modules are missing : {}".format(modules_required)

    if use_colour_text:
       print(Fore.RED + text + Style.RESET_ALL)
    else:
       print(text)

    sys.exit()


def color_print(text):
    if use_colour_text:
        print(Fore.RED + "[WARNING] " + text + Style.RESET_ALL)
    else:
       print("[WARNING] " + text)


def help_manager(func):
    def wrapper(self, *args, **kwargs):
        if len(args) > 0 and args[0] == "?":
            print(func.__doc__)
            return
        return func(self, *args, **kwargs)
    return wrapper


def session_manager(func):
    RENEW_LIMIT = 1000 * 1000 # max. 1800 * 1000 milliseconds or  30 minutes

    def wrapper(self, *args, **kwargs):
        if self.session_token is None:
            self.get_session_token()

        valid_for = self.query_session_token()
        if valid_for is None:
            self.get_session_token()
        elif valid_for < RENEW_LIMIT:
            self.renew_session_token()

        retval = func(self, *args, **kwargs)
        print()
        return retval
    return wrapper


class IData:
    """
    Python interface for http://api.idatamedia.org
    """
    def __init__(self, api_key=None, session_token=None, verbose=False, raw=False, traceback=False):
        self.API_URL = "https://api.idatamedia.org/"
        self.API_KEY = api_key
        self.verbose = verbose
        self.raw = raw
        self.traceback = traceback
        self.session_token = session_token

    def __print_response(self, resp):
        if self.raw is True:
            pprint(resp)

    @help_manager
    def __m(self, text):
        if self.verbose is True:
            if use_colour_text:
                print(Fore.CYAN + "[INFO] " + text + Style.RESET_ALL)
            else:
                print("[INFO] " + text)

    @help_manager
    def __api_call(self, extension="", payload=None, req_mehtod="GET"):
        try:
            if self.verbose is True:
                print ("")
                print (" Verbose is set to ON")
                print("-----------------------------------")
                print (req_mehtod)
                print("URL: ")
                print(self.API_URL)
                print("API: ")
                print(extension)
                print("Payload: ")
                print(payload)


            if req_mehtod == "GET":
                resp = r.get(self.API_URL + extension, params=payload)
            else:
                resp = r.post(self.API_URL + extension, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
            self.__m("API call to: {}, Request mehtod: {}".format(resp.url, req_mehtod))


            resp = resp.json()

            self.__print_response(resp)

        except Exception as e:
            color_print("Unexpected Error: {}".format(e))
            return {}

        errors = resp.get("Errors", None)

        if errors:
            for error in errors:
                error_status = error.get("Status", None)
                error_detail = error.get("Details", None)

                color_print("Error {}: {}".format(error_status, error_detail))

                # if Traceback is set to True, Raise exception
                if self.traceback:
                    raise Exception("Error {}: {}".format(error_status, error_detail))
                else:
                    return {}
        else:
            retval = resp.get("Result", None)

            if retval is None:
                return {}
            return retval

    @help_manager
    def set_verbose(self, verbose):
        """
        If true extra the request details are displayed in the console.
        """
        if bool(verbose):
            self.verbose = True
        else:
            self.verbose = False

        self.__m("Verbose settting updated to {}".format(self.verbose))

        return None

    @help_manager
    def set_return_raw_data(self, raw):
        """
        If true return raw JSON is returned from all server requests.
        """
        if bool(raw):
            self.raw = True
        else:
            self.raw = False

        self.__m("Raw settting updated to {}".format(raw))

        return None

    @help_manager
    def set_traceback(self, traceback: bool):
        """
        If true raises exceptions with traceback detail.
        Otherwise only prints Exception details.
        """
        if traceback:
            self.traceback = True
        else:
            self.traceback = False

        self.__m("Traceback settting updated to {}".format(self.traceback))

        return None

    @help_manager
    def set_api_key(self, API_KEY):
        """
        Register your API key to be able to get a session token.
        """
        if API_KEY:
            self.API_KEY = API_KEY
            self.__m("Stored the new API key {}".format(self.API_KEY))
        else:
            self.__m("You must provide a valid API key.")

        return None

    @help_manager
    def set_api_url(self, API_URL):
        """
        Set the url for the API server
        """
        if API_URL:
            self.API_URL = API_URL
            self.__m("Changed the API URL {}".format(self.API_URL))
        else:
            self.__m("You must provide a valid API address.")

        return None

    @help_manager
    def print_api_key(self):
        """
        Return the API key that was set with the set_api_key command.
        """
        return self.API_KEY

    @help_manager
    def get_api_address(self):
        """
        Returns the API address
        """
        return self.API_URL

    @help_manager
    def get_api_version(self):
        """
        Returns the API version number
        https://www.idatamedia.org/api-docs#apiversion
        """
        resp = self.__api_call("GetAPIVersion")
        return resp.get("Version")

    @help_manager
    def set_session_token(self, session_token):
        """
        Update session token of Idata class instance.
        """
        self.session_token = session_token

        self.__m("Session token updated: {}".format(session_token))

        return session_token

    @help_manager
    def get_session_token(self):
        """
        Get session token of Idata class instance.
        https://www.idatamedia.org/api-docs#sessiontoken
        """

        payload = {
            "APIKey": self.API_KEY,
        }

        self.__m("Retrieving session token using: {}".format(self.API_KEY))
        resp = self.__api_call("GetSessionToken", payload)
        if resp:
            session_token = resp.get("SessionToken", None)
            self.__m("Session token retrieved: {}".format(session_token))

            self.session_token = session_token

            return session_token

    @help_manager
    def query_session_token(self):
        """
        Return the remaining token life in milliseconds.
        https://www.idatamedia.org/api-docs#querysessiontoken
        """
        payload = {
            "SessionToken": self.session_token,
        }

        self.__m("Retrieving expiration time for {}".format(self.session_token))
        resp = self.__api_call("QuerySessionToken", payload)
        if resp:
            remaining = resp.get('Remaining', None)
            self.__m("Remaining {} ms.".format(remaining))

            return remaining

    @help_manager
    def renew_session_token(self):
        """
        Renew the current token to full life.
        https://www.idatamedia.org/api-docs#renewsessiontoken
        """
        payload = {
            "SessionToken": self.session_token,
        }

        self.__m("Renewing session token.")
        resp = self.__api_call("RenewSessionToken", payload)
        if resp:
            self.__m("Session token renewed.")
            session_token = resp.get('SessionToken', None)
            return session_token

    @help_manager
    def revoke_session_token(self):
        """
        Invalidate the current token on the server.
        https://www.idatamedia.org/api-docs#revokesessiontoken
        """
        payload = {
            "SessionToken": self.session_token,
        }
        self.__m("Revoking following session token: {}".format(self.session_token))
        resp = self.__api_call("RevokeSessionToken", payload)
        if resp:
            resp_details = resp.get("Details", None)
            self.__m("{}.".format(resp_details))

            return resp_details

    @help_manager
    def print_session_token(self):
        """
        Returns session token from IData instance.
        """
        return self.session_token

    @session_manager
    @help_manager
    def get_datasource(self,
                       Datasource: str,
                       ReturnCategoryList: Optional[bool] = True,
                       ReturnCategoryTree: Optional[bool] = True,
                       ReturnAccess: Optional[bool] = False,
                       DateFormat: str = "YYYY-MM-DD"
                       ) -> dict:
        """
        Return the metadata for one named datasource.
        https://www.idatamedia.org/api-docs#getonedatasource
        """
        payload = {
            "SessionToken": self.session_token,
            "Datasource": Datasource,
            "ReturnCategoryList": 'true' if ReturnCategoryList else 'false',
            "ReturnCategoryTree": 'true' if ReturnCategoryTree else 'false',
            "ReturnAccess": 'true' if ReturnAccess else 'false',
            "DateFormat": DateFormat
        }

        self.__m("Retreiving datasource for {}".format(Datasource))
        resp = self.__api_call("GetDatasource", payload)
        if resp:
            self.__m("Datasource retrieved.")

            return resp

    @session_manager
    @help_manager
    def get_all_datasources(self,
                       ReturnCategoryList: Optional[bool] = True,
                       ReturnCategoryTree: Optional[bool] = True,
                       ReturnUserCategoryList: Optional[bool] = False,
                       ReturnAccess: Optional[bool] = False,
                       DateFormat: str = "YYYY-MM-DD"
                       ) -> list:
        """
        Return the metadata for all available datasources.
        https://www.idatamedia.org/api-docs#getalldatasource
        """
        payload = {
            "SessionToken": self.session_token,
            "ReturnCategoryList": 'true' if ReturnCategoryList else 'false',
            "ReturnCategoryTree": 'true' if ReturnCategoryTree else 'false',
            "ReturnUserCategoryList" : 'true' if ReturnUserCategoryList else 'false',
            "ReturnAccess": 'true' if ReturnAccess else 'false',
            "DateFormat": DateFormat
        }

        self.__m("Retreiving all datasources...")
        resp = self.__api_call("GetAllDatasources", payload)
        if resp:
            self.__m("Total {} datasources retrieved.".format(len(resp)))

            return resp

    @session_manager
    @help_manager
    def get_user_datasources(self,
                             ReturnCategoryList: Optional[bool] = True,
                             ReturnCategoryTree: Optional[bool] = True,
                             ReturnUserCategoryList: Optional[bool] = False,
                             ReturnAccess: Optional[bool] = False,
                             DateFormat: str = "YYYY-MM-DD") -> list:
        """
        Return the metadata for only the datasources that the user can access.
        https://www.idatamedia.org/api-docs#userdatasource
        """
        payload = {
            "SessionToken": self.session_token,
            "ReturnCategoryList": 'true' if ReturnCategoryList else 'false',
            "ReturnCategoryTree": 'true' if ReturnCategoryTree else 'false',
            "ReturnUserCategoryList" : 'true' if ReturnUserCategoryList else 'false',
            "ReturnAccess": 'true' if ReturnAccess else 'false',
            "DateFormat": DateFormat
        }
        self.__m("Retrieving user datasources.")
        resp = self.__api_call("GetUserDatasources", payload)
        if resp:
            self.__m("Total {} user datasources retrieved.".format(len(resp)))

            return resp

    @session_manager
    @help_manager
    def get_dataset_of(self,
                       Datasource: str,
                       Filter: Optional[str] = None,
                       CaseSensitive: Optional[bool] = None,
                       SortOrder: Optional[str] = None,
                       SortColumns: Optional[str] = None,
                       IgnoreEmpty: Optional[bool] = None,
                       ShortRecord: Optional[bool] = None,
                       ReturnCategoryTree: Optional[bool] = None,
                       ReturnCategoryList: Optional[bool] = None,
                       ReturnUserCategoryList: Optional[bool] = None,
                       CategoryFilter: Optional[str] = None,
                       Page: Optional[int] = None,
                       Rows: Optional[int] = None,
                       ValuesSince: Optional[str] = None) -> dict:
        """
        Retrieve the metadata for all (or some) of the datasets in one datasource.
        https://www.idatamedia.org/api-docs#datasetsonesource
        """

        payload = {
            "SessionToken":             self.session_token,
            "Datasource":               Datasource,
            "Filter":                   Filter,
            "CaseSensitive":            None if CaseSensitive is None else str(CaseSensitive).lower(),
            "SortOrder":                SortOrder,
            "SortColumns":              SortColumns,
            "IgnoreEmpty":              None if IgnoreEmpty is None else str(IgnoreEmpty).lower(),
            "ShortRecord":              None if ShortRecord is None else str(ShortRecord).lower(),
            "ReturnCategoryTree":       None if ReturnCategoryTree is None else str(ReturnCategoryTree).lower(),
            "ReturnCategoryList":       None if ReturnCategoryList is None else str(ReturnCategoryList).lower(),
            "ReturnUserCategoryList":   None if ReturnUserCategoryList is None else str(ReturnUserCategoryList).lower(),
            "CategoryFilter":           CategoryFilter,
            "Page":                     Page,
            "Rows":                     Rows,
            "ValuesSince":              ValuesSince,
        }
        self.__m("Retrieving datasets for {}.".format(Datasource))
        resp = self.__api_call("GetDatasets", payload)
        if resp:
            self.__m("Datasets retrieved.")
            return resp

    @session_manager
    @help_manager
    def get_datasets(self,
                     Datasource: str,
                     SessionToken: Optional[str] = None,
                     Filter: Optional[str] = None,
                     CategoryFilter: Optional[str] = None,
                     CaseSensitive: Optional[bool] = False,
                     SortOrder: Optional[str] = 'asc',
                     SortColumns: Optional[str] = 'Symbol',
                     IgnoreEmpty: Optional[bool] = False,
                     ShortRecord: Optional[bool] = False,
                     Page: Optional[int] = 1,
                     Rows: Optional[int] = 100,
                     ValuesSince: Optional[str] = None,
                     DateFormat: Optional[str] = 'YYYY-MM-DD',
                     ReturnAccess: Optional[bool] = False) -> dict:
        """
        Return metadata for the datasets in one datasource
        https://www.idatamedia.org/api-docs#datasetsonesource
        """

        payload = {
            "SessionToken": SessionToken if SessionToken else self.session_token,
            "Datasource": Datasource,
            "CaseSensitive": 'true' if CaseSensitive else 'false',
            "SortOrder": SortOrder,
            "SortColumns": SortColumns,
            "IgnoreEmpty": 'true' if IgnoreEmpty else 'false',
            "ShortRecord": 'true' if ShortRecord else 'false',
            "Page": Page,
            "Rows": Rows,
            "DateFormat": DateFormat,
            "ReturnAccess": 'true' if ReturnAccess else 'false',
        }
        if Filter:
            payload['Filter'] = Filter
        if CategoryFilter:
            payload['CategoryFilter'] = CategoryFilter
        if ValuesSince:
            payload['ValuesSince'] = ValuesSince

        self.__m("Retrieving datasets")
        resp = self.__api_call("GetDatasets", payload)
        if resp:
            self.__m("Datasets retrieved.")

            return resp

    @session_manager
    @help_manager
    def get_selected_datasets(self,
                             Series: list,
                             SessionToken: Optional[str] = None,
                             ShortRecord: Optional[bool] = False,
                             ValuesSince: Optional[str] = None,
                             ReturnAccess: Optional[bool] = False,
                             DateFormat: Optional[str] = 'YYYY-MM-DD'
                             ) -> dict:
        """
        Return metadata for multiple named datasets in one or more datasources.
        https://www.idatamedia.org/api-docs#datasetsmultiplesources
        """

        payload = {
            "SessionToken": SessionToken if SessionToken else self.session_token,
            "Series[]":Series,
            "ShortRecord": 'true' if ShortRecord else 'false',
            "DateFormat": DateFormat,
            "ReturnAccess": 'true' if ReturnAccess else 'false',
        }
        if ValuesSince:
            payload['ValuesSince'] = ValuesSince

        self.__m("Retrieving datasets")
        resp = self.__api_call("GetSelectedDatasets", payload, "POST")
        if resp:
            self.__m("Datasets retrieved.")

            return resp

    @session_manager
    @help_manager
    def get_user_favorites_status(self):
        """
        Return the server date and time that the user favorites list was last changed.
        https://www.idatamedia.org/api-docs#favoritestatus
        """
        payload = {
            "SessionToken": self.session_token,
        }

        resp = self.__api_call("GetFavoritesStatus", payload)
        if resp:
            return resp

    @session_manager
    @help_manager
    def get_user_favorites(self,
                      SessionToken: Optional[str] = None,
                      IgnoreEmpty: bool = False,
                      ReturnFavoritesTree: Optional[bool] = False,
                      ReturnAccess: Optional[bool] = False,
                      Page: Optional[int] = 1,
                      Rows: Optional[int] = 50,
                      DateFormat: Optional[str] = "YYYY-MM-DD") -> dict:
        """
        Return metadata for all the datasets in the user favorites list.
        https://www.idatamedia.org/api-docs#favoritesmetadata
        """
        payload = {
            "SessionToken": SessionToken if SessionToken else self.session_token,
            "IgnoreEmpty": "true" if IgnoreEmpty else "false",
            "ReturnFavoritesTree": "true" if ReturnFavoritesTree else "false",
            "ReturnAccess": "true" if ReturnAccess else "false",
            "Page": Page,
            "Rows": Rows,
            "DateFormat": DateFormat,
        }

        self.__m("Retrieving user favorites.")
        resp = self.__api_call("GetUserFavorites", payload)
        if resp:
            self.__m("User favorites retrieved.")

            return resp

    @session_manager
    @help_manager
    def add_user_favorites(self,
                           Series: list,
                           SessionToken: str = None):
        """
        Add datasets to the user favorites list.
        https://www.idatamedia.org/api-docs#adddatasetstofavorites
        """

        payload = {
            "SessionToken": SessionToken if SessionToken else self.session_token,
            "Series[]": Series,
        }

        self.__m("Adding {} to favorites.".format(', '.join(Series)))
        resp = self.__api_call("AddFavorites", payload, "POST")
        if resp:
            status_code = resp.get("Status", None)
            detail = resp.get("Detail", None)

            if status_code == 204:
                self.__m("This symbol is already in  the User Favorites. Request ignored.")
            elif status_code == 200:
                self.__m("A new symbol was successfully added.")
            else:
                self.__m("Unknown status code: {}, {}".format(status_code, detail))

            return resp

    @session_manager
    @help_manager
    def remove_user_favorites(self,
                              Series: list,
                              SessionToken: str = None) -> dict:
        """
        Remove datasets from your user favorites list.
        https://www.idatamedia.org/api-docs#removedatasetfromfavorites
        """

        payload = {
            "SessionToken": SessionToken if SessionToken else self.session_token,
            "Series[]": series,
        }

        self.__m("Removing {} from favorites.".format(', '.join(Series)))
        resp = self.__api_call("RemoveFavorites", payload, "POST")
        if resp:
            status_code = resp.get("Status", None)
            detail = resp.get("Detail", None)

            if status_code == 204:
                self.__m("This symbol is not in the User Favorites. Request ignored.")
            elif status_code == 200:
                self.__m("New symbol successfully deleted.")
            else:
                self.__m("Unknown status code: {}, {}".format(status_code, detail))

            return resp

    @session_manager
    @help_manager
    def get_dataset_values(self,
                           Series: list,
                           SessionToken: str = None,
                           StartDate: Optional[str] = "Earliest",
                           EndDate: Optional[str] = "Latest",
                           Periods: Optional[int] = 0,
                           CommonStart: Optional[bool] = False,
                           CommonEnd: Optional[bool] = False,
                           CommonUA: Optional[bool] = True,
                           DateFormat: Optional[str] = "YYYY-MM-DD",
                           DateOrder: Optional[str] = "asc",
                           Prefill: Optional[bool] = False,
                           Fill: Optional[bool] = False,
                           Frequency: Optional[str] = 'd',
                           Postfill: Optional[bool] = False,
                           Rounding: Optional[str] = 'auto',
                           ReturnMetadata: Optional[bool] = False,
                           ReturnAccess: Optional[bool] = False,
                           ReturnParameters: Optional[bool] = False,
                           ReturnBateStatus: Optional[bool] = False,
                           PrefillOptions: Optional[dict] = None,
                           FillOptions: Optional[dict] = None,
                           FrequencyOptions: Optional[dict] = None,
                           PostFillOptions: Optional[dict] = None,
                           Sparse: Optional[str] = None,
                           SparseOptions: Optional[dict] = None,
                           NAValue: Optional[Any] = None) -> list:
        """
        Return a range of dataset values (or averages for named datasets in one or more datasources.
        https://www.idatamedia.org/api-docs#getdatasetvalues
        """

        payload = {
#         "SessionToken": session_token if session_token else self.session_token,
           "SessionToken": SessionToken if SessionToken else self.SessionToken,
            "Series": Series,
            "StartDate": StartDate,
            "EndDate": EndDate,
            "Periods": Periods,
            "CommonStart": str(CommonStart).lower(),
            "CommonEnd": str(CommonEnd).lower(),
            "CommonUA": str(CommonUA).lower(),
            "DateFormat": DateFormat,
            "DateOrder": DateOrder,
            "Prefill": str(Prefill).lower(),
            "Fill": str(Fill).lower(),
            "Frequency": str(Frequency.lower()),
            "Postfill": str(Postfill).lower(),
            "Rounding": Rounding,
            "ReturnMetadata": str(ReturnMetadata).lower(),
            "ReturnAccess": str(ReturnAccess).lower(),
            "ReturnParameters": str(ReturnParameters).lower(),
            "ReturnBateStatus": str(ReturnBateStatus).lower(),
        }

        if PrefillOptions:
            payload['PrefillOptions'] = PrefillOptions

        if FillOptions:
            payload['FillOptions'] = FillOptions

        if FrequencyOptions:
            payload['FrequencyOptions'] = FrequencyOptions

        if PostFillOptions:
            payload['PostFillOptions'] = PostFillOptions

        if Sparse:
            payload['Sparse'] = Sparse

        if SparseOptions:
            payload['SparseOptions'] = SparseOptions

        if NAValue:
            payload['NAValue'] = NAValue

        resp = self.__api_call("GetValues", payload, "POST")
        if resp:
            return resp


    @session_manager
    @help_manager
    def get_dataset_values_rc(self,
                           Series: list,
                           SessionToken: str = None,
                           StartDate: Optional[str] = "Earliest",
                           EndDate: Optional[str] = "Latest",
                           Periods: Optional[int] = 0,
                           CommonStart: Optional[bool] = False,
                           CommonEnd: Optional[bool] = False,
                           CommonUA: Optional[bool] = True,
                           DateFormat: Optional[str] = "YYYY-MM-DD",
                           DateOrder: Optional[str] = "asc",
                           Prefill: Optional[bool] = False,
                           Fill: Optional[bool] = False,
                           Frequency: Optional[str] = 'd',
                           Postfill: Optional[bool] = False,
                           Rounding: Optional[str] = 'auto',
                           ReturnMetadata: Optional[bool] = False,
                           ReturnAccess: Optional[bool] = False,
                           ReturnParameters: Optional[bool] = False,
                           PrefillOptions: Optional[dict] = None,
                           FillOptions: Optional[dict] = None,
                           FrequencyOptions: Optional[dict] = None,
                           PostfillOptions: Optional[dict] = None,
                           Sparse: Optional[str] = None,
                           SparseOptions: Optional[dict] = None,
                           NAValue: Optional[Any] = None) -> list:


        payload = {
        #         "SessionToken": session_token if session_token else self.session_token,
           "SessionToken": SessionToken if SessionToken else self.session_token,
            "Series": Series,
            "StartDate": StartDate,
            "EndDate": EndDate,
            "Periods": Periods,
            "CommonStart": str(CommonStart).lower(),
            "CommonEnd": str(CommonEnd).lower(),
            "CommonUA": str(CommonUA).lower(),
            "DateFormat": DateFormat,
            "DateOrder": DateOrder,
            "Prefill": str(Prefill).lower(),
            "Fill": str(Fill).lower(),
            "Frequency": str(Frequency).lower(),
            "Postfill": str(Postfill).lower(),
            "Rounding": Rounding,
            "ReturnMetadata": str(ReturnMetadata).lower(),
            "ReturnAccess": str(ReturnAccess).lower(),
            "ReturnParameters": str(ReturnParameters).lower(),
        }

        if PrefillOptions:
            payload['PrefillOptions'] = PrefillOptions

        if FillOptions:
            payload['FillOptions'] = FillOptions

        if FrequencyOptions:
            payload['FrequencyOptions'] = FrequencyOptions

        if PostfillOptions:
            payload['PostfillOptions'] = PostfillOptions

        if Sparse:
            payload['Sparse'] = Sparse

        if SparseOptions:
            payload['SparseOptions'] = SparseOptions

        if NAValue:
            payload['NAValue'] = NAValue



        """
        As get_dataset_values above but returned formatted row x column.
        https://www.idatamedia.org/api-docs#getdatasetvaluesrc
        """


        resp = self.__api_call("GetValuesRC", payload, "POST")

        if resp:
            return resp

    @session_manager
    @help_manager
    def get_dataset_values_for_date(self,
                                    Series: list,
                                    Date: str,
                                    SessionToken: str = None,
                                    ReturnLatest: Optional[bool] = False,
                                    ReturnCorrections: Optional[bool] = True,
                                    DateFormat: Optional[str] = 'YYYY-MM-DD',
                                    Rounding: Optional[str] = 'auto',
                                    Frequency: Optional[str] = 'd',
                                    ReturnAccess: Optional[bool] = False,
                                    ReturnBateNames: Optional[bool] = False,
                                    ReturnBateStatus: Optional[bool] = False,
                                    ReturnMetadata: Optional[bool] = False,
                                    ReturnParameters: Optional[bool] = False,
                                    FrequencyOptions: Optional[dict] = None,
                                    SparksCount: Optional[int] = None
                                    ) -> list:
        """
        Return dataset values (or averages)for named datasets (in one or more datasources) for a single date.
        https://www.idatamedia.org/api-docs#getdatasetvaluesforadate
        """

        payload = {
            "SessionToken": SessionToken if SessionToken else self.SessionToken,
            "Series[]": Series,
            "Date": Date,
            "ReturnLatest": str(ReturnLatest).lower(),
            "ReturnCorrections": str(ReturnCorrections).lower(),
            "DateFormat": DateFormat,
            "Rounding": Rounding,
            "Frequency": str(Frequency).lower(),
            "ReturnAccess": str(ReturnAccess).lower(),
            "ReturnBateNames": str(ReturnBateNames).lower(),
            "ReturnBateStatus": str(ReturnBateStatus).lower(),
            "ReturnMetadata": str(ReturnMetadata).lower(),
            "ReturnParameters": str(ReturnParameters).lower(),
        }

        if SparksCount:
            payload['SparksCount'] = SparksCount

        if FrequencyOptions:
            payload['FrequencyOptions'] = FrequencyOptions

        resp = self.__api_call("GetValuesForDate", payload, "POST")
        if resp:
            return resp

    @session_manager
    @help_manager
    def get_my_account_details(self):
        """
        Return registered user account details including API key.
        https://www.idatamedia.org/api-docs#getmyaccountdetails
        """
        payload = {
            "SessionToken": self.session_token,
        }

        self.__m("Retrieving account details.")
        resp = self.__api_call("GetAccountDetails", payload)
        if resp:
            self.__m("Account details retrieved.")

            return resp

    @session_manager
    @help_manager
    def request_new_api_key(self):
        """
        Return a new API key (the current one will be invalidated!).
        https://www.idatamedia.org/api-docs#newapikey
        """
        payload = {
            "SessionToken": self.session_token,
        }

        self.__m("Requesting new API Key...")
        resp = self.__api_call("RequestNewAPIKey", payload)
        if resp:
            new_api_key = resp.get("APIkey", None)

            self.__m("New API Key returned. {}.".format(new_api_key))
            self.API_KEY = new_api_key
            self.__m("New API Key was reset to default")
            return new_api_key

    @session_manager
    @help_manager
    def send_reset_password(self, email):
        """
        Request to reset your password using an emailed link.
        https://www.idatamedia.org/api-docs#resetpassword
        """
        payload = {
            "Email": email,
        }

        self.__m("Resetting password...")
        resp = self.__api_call("SendPasswordReset", payload)
        if resp:
            status_code = resp.get("Status", None)
            detail = resp.get("Detail", None)

            if status_code == 200:
                self.__m("Password reset successful. {}".format(detail))
            else:
                self.__m("Password reset failed. {}".format(detail))
            return detail
