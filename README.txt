Introduction
============


This product provides a couple IOrdering adpaters to provide efficient
auto-sorting of folders with significant amounts of content.

It includes a title (``flexible-title-ordering``) and id
(``flexible-id-ordering``) ordering, but is intended to allow easy
creation of custom sorts.

It is easy to create custom ordering implementations by subclassing
one of the included implementations and simply overriding the
``key_func(obj)`` method which generates a sort key for contained
content.  Essentially, any ordering can be achieved in this manner.

Note: The full data structure containing the folder order key -> id
mapping is stored on the folder itself.  This means that folder
instances with a large amount of content may become somewhat large,
but that order lookups should be quite fast.

Credits
-------


Alec Mitchell
Jazkarta, Inc.

With thanks to:
Dumbarton Oaks
KCRW Radio
