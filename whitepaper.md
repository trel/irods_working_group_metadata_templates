# motivation

irods needs to help curators define and validate 'good' metadata for their pipelines/environments

# history

metalnx

cloudbrowser

skarbez

swagger API


# conclusions


iRODS should focus on the capabilities and functionality, rather than defining policy/schemas on applications and users

iRODS should define the framework (policies and PEPs)

"Agnostic"

Swagger API -> OpenAPI rebranding

 - List attached MTs on an object/collection
 - Attach/Apply MT to an object/collection as required/optional
 - Remove MT from an object/collection
 - Resolve instance of MT based on an object/collection JSON
 - Resolve json schema(s) that defines the metadata to be applied via template X to collection Y
 - BONUS - Rasterize / Pre-assemble? Set of nested/attached schemas down into a single schema


iRODS can't/shouldn't be defining the templates for anyone?

 - Site-specific knowledge and interfaces are too diverse

PEPs / microservices / functions to validate, but not manage the templates themselves

 - Template management is too big a task for the server/policy


# future work

Consider breaking apart the functionality of what a template does

 - Annotation
 - Validation
 - External references
 - Define parent/child relationships between metadata elements
   - Recursive query syntax of SQL

These parts together could be stitched together on a per site/application

 - Provide 70-80% of the original intent of metadata templates

