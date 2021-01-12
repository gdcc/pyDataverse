.. _community_faq:

Frequently Asked Questions
==================================

**Q: What is a "Dataverse"?**

A: Dataverse has two meanings. 1. Dataverse is the name of the data repository software. 2. It's the top-level data type in Dataverse, the data repository software..

**Q: What is a Dataset?**

A: A Dataset is a collection of Datafiles. This means, it is not just the
data itself, as the term is often used for, but it is the whole collection
of data. This includes the data itself, but also the documentation, the
codebook or other additional Datafiles.

**Q: What is a Datafile?**

A: A Datafile is a Dataverse data type. It consists of the file itself, and
the metadata of it. A Datafile is always part of a Dataset.

**Q: What are the expected HTTP Status Codes for the API requests?**

A: This is so far not really documented. There is an issue created for this,
but we are trying to crowdsource this. So please add your knowledge to our
`Wiki page <https://github.com/AUSSDA/pyDataverse/wiki/API-Responses>`_
or get in touch with us through our :ref:`community_contact`.

**Q: Can I create my own API calls?**

A: Yes. You can use the basic :class:Api request functions
(:meth:Api.get_request(), :meth:Api.post_request(), :meth:Api.put_request(),
:meth:Api.delete_request()) and pass your own query-string, metadata as parameters.
