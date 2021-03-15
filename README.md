# Cirrus Task Template

This repository is a template for creating new Cirrus tasks, either as Lambda functions or as a Batch job.

Tasks can be run locally as they include a CLI:

```
$ task.py -h
```

When run in Cirrus they use the `cirrus` subcommand to pass in the payload s3 location:

```
$ task.py cirrus s3://bucket/prefix/payload.json
```

While when run locally use the `local` subcommand, specify a local payload, and optionally provide a working directory

```
$ task.py local payload.json --workdir test-run/
```

When run locally the handler will not upload assets to s3. It will also not remove the working directory when it completes.


## About

Cirrus is an open-source pipeline for processing geospatial data in AWS. Cirrus was developed by [Element 84](https://element84.com/) originally under a [NASA ACCESS project]. It is released under the Apache License.
