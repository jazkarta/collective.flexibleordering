Introduction
============


This product provides an IOrdering adpaters to provide efficient
auto-sorting of folders with significant amounts of content.

It includes a title (``flexible-title-ordering``) and id
(``flexible-id-ordering``) ordering, but is intended to allow easy
creation of custom sorts.

These orderings internally lookup another adapter (``IOrderingKey``)
on the folder which provides sort key generation for contained
objects.

As a result, it is possible to customize ordering, either by providing
a more specific version of the ``IOrderingKey`` adapter for a specific
folder, or by using one of the existing ``IOrdering`` implementations
as a base for a new ordering.  Essentially, any ordering can be
achieved in this manner.


Credits
-------

Alec Mitchell
Jazkarta, Inc.

With thanks to:
Dumbarton Oaks
KCRW Radio
