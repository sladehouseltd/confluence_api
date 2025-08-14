# [Feature/System Name]

I want to create a python script that uses the Confluence API to look at all pages in a space and work out the last time they were modified.  If possible, I would also like to see the last time all pages in a space were viewed.


## Requirements

*List the specific, measurable acceptance criteria that define when this feature is complete. These should be testable and unambiguous. Think of these as your definition of done.*

* A script can be called with the following arguments.
** Confluence space
** date_modified
** date_viewed
* If date_modifed, a csv is create shwowing the most recent date modified for all pages in the given space
* If date_viewed, a csv is create showing the most recent date viewed for all pages in the given space
* The csv would be sorted by the date field descending
* The csv would have two columns, page and date_viewed or date_modified
* If both date_viewed and date_modified given the CSV would have three columns - page and date_viewed and date_modified

## Rules

*Specify any rules files that should be included when working on this feature. This includes any relevant rule files for implementing this slice. The rules files are usually found under the `rules/` directory of this project.*

## Domain

*If applicable, describe the core domain model using pseudo-code in a modern language like TypeScript or Kotlin. Focus on the key entities, relationships, and business logic. This section helps establish the mental model for the feature.*

// Core domain representation in markdown block

## Extra Considerations

*List important factors that need special attention during implementation. This often grows as you discover edge cases or constraints during development. Think about non-functional requirements, constraints, or gotchas.*

- 

## Testing Considerations

*Describe how you want this feature to be tested. What types of tests are needed? What scenarios should be covered? What are the quality gates?*

* acceptance tests

## Implementation Notes

*Document your preferences for how this should be built. This might include architectural patterns, coding standards, technology choices, or specific approaches you want followed.*

* python script
* I would like to follow the config set up shown in https://github.com/sladehouseltd/jira-api-cycle-times. That is an env file with confluence URL, username and password that are used by the script.  I would like to follow the convention of if no values or no env file, then the user has to type their username and password in.


## Specification by Example

*Provide concrete examples of what the feature should do. This could be API request/response examples, Gherkin scenarios, sample CSV representation, or user interaction flows. Make the abstract requirements tangible.*




## Verification

*Create a checklist to verify that the feature is complete and working correctly. These should be actionable items that can be checked off systematically.*

* date_modified option creates a csv with the two columns mentioned above.  Contains all the pages in the given space.  Two columns correctly poplulated
* date_viewed option creates a csv with the two columns mentioned above.  Contains all the pages in the given space.  Two columns correctly poplulated
* date_modified and date_viewed option creates a csv with the three columns mentioned above.  Contains all the pages in the given space.  Three columns correctly poplulated

