.. _community_faq:

FAQ
==================================

**Q: What is the "Dataverse Software?" What is a "Dataverse collection?"**

A: The Dataverse Software is the name of the open source
data repository software. 2. A Dataverse collection is the top-level data-type in the
Dataverse Software.

**Q: What is a "Dataset"?**

A: The term dataset differs from the usual use for a structured set of data.
A Dataset in the Dataverse software is a data-type typically representative for all content of one study.
The Dataset itself contains only metadata, but it relates to other data-types:
Datafiles are attached to it and a Dataset is always part of a Dataverse collection.

**Q: What is a "Datafile"?**

A: A Datafile is a Dataverse software data-type. It consists of the file itself and
its metadata. A Datafile is always part of a Dataset.

**Q: What are the expected HTTP Status Codes for the API requests?**

A: So far, this is still an unsolved question, as it is not documented yet.
We started to collect this information at a
`Wiki page <https://github.com/gdcc/pyDataverse/wiki/API-Responses>`_
, so if you have some knowledge about this, please add it there
or get in touch with us (:ref:`community_contact`).

**Q: Can I create my own API calls?**

A: Yes, you can use the :class:`Api <pyDataverse.api>` base-class and its request functions
(:meth:`get_request() <pyDataverse.api.get_request>`, :meth:`post_request() <pyDataverse.api.post_request>`, :meth:`put_request() <pyDataverse.api.put_request>` and
:meth:`delete_request() <pyDataverse.api.delete_request>`) and pass your own parameter.
