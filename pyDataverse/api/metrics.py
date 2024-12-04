from pyDataverse.api.api import Api, DEPRECATION_GUARD


class MetricsApi(Api):
    """Class to access Dataverse's Metrics API.

    Attributes
    ----------
    base_url_api_metrics : type
        Description of attribute `base_url_api_metrics`.
    base_url : type
        Description of attribute `base_url`.

    """

    def __init__(self, base_url, api_token=None, api_version="latest", *, auth=None):
        """Init an MetricsApi() class."""
        super().__init__(base_url, api_token, api_version, auth=auth)
        if base_url:
            self.base_url_api_metrics = "{0}/api/info/metrics".format(self.base_url)
        else:
            self.base_url_api_metrics = None

    def total(self, data_type, date_str=None, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/$type
        GET https://$SERVER/api/info/metrics/$type/toMonth/$YYYY-DD

        $type can be set to dataverses, datasets, files or downloads.

        """
        url = "{0}/{1}".format(self.base_url_api_metrics, data_type)
        if date_str:
            url += "/toMonth/{0}".format(date_str)
        return self.get_request(url, auth=auth)

    def past_days(self, data_type, days_str, auth=DEPRECATION_GUARD):
        """

        http://guides.dataverse.org/en/4.18.1/api/metrics.html
        GET https://$SERVER/api/info/metrics/$type/pastDays/$days

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/{1}/pastDays/{2}".format(
            self.base_url_api_metrics, data_type, days_str
        )
        return self.get_request(url, auth=auth)

    def get_dataverses_by_subject(self, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/dataverses/bySubject

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/dataverses/bySubject".format(self.base_url_api_metrics)
        return self.get_request(url, auth=auth)

    def get_dataverses_by_category(self, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/dataverses/byCategory

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/dataverses/byCategory".format(self.base_url_api_metrics)
        return self.get_request(url, auth=auth)

    def get_datasets_by_subject(self, date_str=None, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/datasets/bySubject

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/datasets/bySubject".format(self.base_url_api_metrics)
        if date_str:
            url += "/toMonth/{0}".format(date_str)
        return self.get_request(url, auth=auth)

    def get_datasets_by_data_location(self, data_location, auth=DEPRECATION_GUARD):
        """
        GET https://$SERVER/api/info/metrics/datasets/?dataLocation=$location

        $type can be set to dataverses, datasets, files or downloads.
        """
        # TODO: check if date-string has proper format
        url = "{0}/datasets/?dataLocation={1}".format(
            self.base_url_api_metrics, data_location
        )
        return self.get_request(url, auth=auth)
