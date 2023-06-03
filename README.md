# Purpose of conway module

The `conway` module prescribes patterns for a category of Python applications targeting use cases
involving the need to automate pipeplines and workflows to manipulate a number of Excel spreadsheets.

For example, a typical application would source Excel spreadsheets from some upstream system, and then
use them as input to a data science pipeline that through analysis, enrichment and data manipulation would
result in the creation of other Excel spreadsheets, possibly targetting specific types of personas.

These spreadsheets would typically adhere to a "schema", i.e., there would be a domain model defining specific
"data types" and each Excel spreadsheet would adhere to one such "data types", codifyied through the specification
that Excel files of a given "data type" must contain certain columns and probably be in a filename adhering to 
naming conventions for such "data type". These are assumptions that will be relied upon by the application's
business logic.

For example, a common "data type" would be a type of Excel report R that describes progress for a product.
Then we could have different logical data objects X, Y, Z, .., all of the same "data type" R, where X, Y, Z, ..
represent product-specific reports.

The relationship between logical data objects X, Y, .. to Excel spreadsheets is 1-to-many (as opposed to 1-1)
because these applications also have a notion of "timestamp". 

Thus, each logical data object X  has a lifecycle spanning multiple timestamps t1, t2, ..., and there would
be different Excel files per timestmap, which we refer to as X@t1, X@t2, ...

This temporal dimension is factored in the functionality of the business logic of the application's pipelines. For example:

* A pipeline might use a timestamp parameter t1 and constrain all input and output spreadsheets to be as of t1

* Another pipeline may take two timestamps t1 and t1, and logical pieces of data X, Y, and output
  Y@t2 based on inputs X@t1, X@t2. For example, Y might be "a report on the difference in X between t1 and t2".

This temporal capability allow such applications to feedback loops, which in turns makes it possible to support
"workflows", not just "pipelines". The distinction is as follows:

* A "pipeline" is just an automated sequence of steps that takes inputs X, Y, .. and produces outputs A, B, ...,
  where none of the inputs is also an output.

* A "workflow" allows for some outputs to also be inputs, as long as it is from a prior timestamp (to ensure it exist).
  For example, consider pipeline that for any time t produces output Y@t based on input X@t. This can be modified
  to a workflow by changing the business logic so that for times t1 < t2, the logic computes Y@t2 based on X@t2 and Y@t1

A typical application of "workflows" is to support annotations. For example, the application might be generating
Excel reports X1, X2, ...with tasks for users U1, U2, ...
It might be that some users may disagree that some of the tasks belongs to them, and feel it should have been routed to someone else.
In that case, the application could offer functionality for users to "annotate" a column in their Excel report. For example,
perhaps user U1 modifies the generated report X1@t1 by putting user U2 in an otherwise blank column called "Re-route to".
Then the next time t2 that the business logic runs, it can consult the "annotation" by using X1@t1 as one of its inputs and
have that task appear in X2@t2 instead of X1@t2. We could say the "task was re-routed from X1 to X2". The users would experience it
as "the task user U1 got at t1 got re-assigned to user U2 at t2".

This completes the examples of the capabilities and patterns expected from applications built using this chassis.

# Data Hubs for Excel file organization

Applications using the `conway` manipulate many excel spreadsheets. There are three dimensions driving the
volumne:

* The types in the application's domain model: R, S, ...

* For each type R, the logical data objects of R: X, Y, ...

* For logical object X and each timestamp t1, t2, ..., the specific Excel spreadsheets X@t1, X2t2, ...

There is an additional, higher-level dimension, that we call the "dat hubs". Typically, the domain model types R, S, ..
are grouped into taxonomies. For example:

* Some types correspond to data integrated from other data sources A, B, .... For example, perhaps types
  R1, R2 are for data sourced from an upstream system A, while types R3, R4 might be integrated from an external data provider
  B. We would model A and B as "data hubs" in our domain model.

* Some types correspond to different internal stakeholder organizations O, P, ... For example, some types are for reports 
  published to executives E, and other types are for more detailed reports published to the heads of different product teams
  P1, P2

The domain concept of "data hub" represents this. An application typically partitions data types into a taxonomy of 
"data hubs", and the questions of  "where did the data come from" and "who will be consuming this data" are answered by
looking at where the data fits in the data hub taxonomy.

Consider again the example above, where we have data sources A, B, .. and internal executive stakeholdesr E, P1, P2, P3, ..
Applications are expected to model this using a class hierarchy, but it is up to an application's designers to decide whether to push
granularity to the class hierarchy design, or to the number of fields in each class. For example:

* One design could just have two classes: Sources and Publications. The attributes of these two classes would be ideated so that
  the Sources class can represet A, B, while the attributes of the Publicatinos class should be able to represent E, P1, P2, ...

* Another design might have a class SourceA for A, SourceB for B, ExecutivesArea for E, and ProductArea for P1, P2, ...

Whatever the design is, the materialization of storage for the Excel spreadsheets is typically the file system. Therefore, what 
the data hub taxonomies define is that folder structure.

For example, suppose that the application designers have opted for a single class Publication for storing the Excel files
generated for stakeholders E, P1, P2, .... Suppose further that there are different kinds of product reports, like "Plans"
and "Dashboards".

Then the Publication class might have attributes to represent a storage structure like:

ROOT
  |--- executive_reports
  |--- p1
  |     |--- Plans
  |     |--- Dashboards
  |
  |--- p2
  |     |--- Plans
  |     |--- Dashboards
  |

