# Cromulent (CROM) Change Log

Any notable changes to CROM that affect either functionality or output will be documented in this file (the format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)).

## [Unreleased] 2020-11-03

## Added

* Added this change log [[DEV-6985](https://jira.getty.edu/browse/DEV-6985)].

* Reinstated the `Relationship` entity and its associated properties `relates_to`, `relates_from`, `related_to_by`, and `related_from_by` as these are in production data modelling use, as their sudden removal led to runtime exceptions and prevented code reliant on CROM from operating [[DEV-6985](https://jira.getty.edu/browse/DEV-6985)].

* Reinstated the `Geometry` and `CoordinateSystem` entities as these are in production data modelling use, as their sudden removal led to runtime exceptions and prevented code reliant on CROM from operating [[DEV-6985](https://jira.getty.edu/browse/DEV-6985)].

* Reinstated the `current_keeper` and `current_keeper_of` properties as these are in production data modelling use, as their sudden removal led to runtime exceptions and prevented code reliant on CROM from operating [[DEV-6985](https://jira.getty.edu/browse/DEV-6985)].

## Changed

* Imported the updated Getty-local `linked-art.json` context document from the `getty-contexts` repository to ensure consistency [[DEV-6984](https://jira.getty.edu/browse/DEV-6984)].
