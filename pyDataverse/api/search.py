from pyDataverse.api.api import Api, DEPRECATION_GUARD


class SearchApi(Api):
    """Class to access Dataverse's Search API.

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    Attributes
    ----------
    base_url_api_search : type
        Description of attribute `base_url_api_search`.
    base_url : type
        Description of attribute `base_url`.

    """

    def __init__(self, base_url, api_token=None, api_version="latest", *, auth=None):
        """Init an SearchApi() class."""
        super().__init__(base_url, api_token, api_version, auth=auth)
        if base_url:
            self.base_url_api_search = "{0}/search?q=".format(self.base_url_api)
        else:
            self.base_url_api_search = self.base_url_api

    def search(
        self,
        q_str,
        data_type=None,
        subtree=None,
        sort=None,
        order=None,
        per_page=None,
        start=None,
        show_relevance=None,
        show_facets=None,
        filter_query=None,
        show_entity_ids=None,
        query_entities=None,
        auth=DEPRECATION_GUARD,
    ):
        """Search.

        http://guides.dataverse.org/en/4.18.1/api/search.html
        """
        url = "{0}{1}".format(self.base_url_api_search, q_str)
        if data_type:
            # TODO: pass list of types
            url += "&type={0}".format(data_type)
        if subtree:
            # TODO: pass list of subtrees
            url += "&subtree={0}".format(subtree)
        if sort:
            url += "&sort={0}".format(sort)
        if order:
            url += "&order={0}".format(order)
        if per_page:
            url += "&per_page={0}".format(per_page)
        if start:
            url += "&start={0}".format(start)
        if show_relevance:
            url += "&show_relevance={0}".format(show_relevance)
        if show_facets:
            url += "&show_facets={0}".format(show_facets)
        if filter_query:
            url += "&fq={0}".format(filter_query)
        if show_entity_ids:
            url += "&show_entity_ids={0}".format(show_entity_ids)
        if query_entities:
            url += "&query_entities={0}".format(query_entities)
        return self.get_request(url, auth=auth)
