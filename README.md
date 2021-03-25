# Cirrus Task Template

This repository is a template for creating new Cirrus tasks, either as Lambda functions or as a Batch job.

## Deployment

Include this task in a workflow by including the Lambda deployment package URL or the Docker image name for Batch.

### Lambda

| Version     | Package URL (Lambda)     | Image Name (Batch) |
| ----------- | ------------------------ | ------------------ |
| 0.2.0       | https://url/to/zip/file  | org/image:tag      |

## Usage

Configuration parameters are available in the Cirrus payload under `payload['process']['tasks']['<taskname>']`. The following parameters are available:

| Field       | Type     | Description |
| ----------- | -------- | ----------- |
| assets      | Map<string, ConvertAsset Object> | **REQUIRED** Dictionary of Asset keys to convert with parameters for each asset |
| drop_assets | [string] | Asset keys to remove from output STAC Item(s) (Default: [])  |

Additionally this task creates files that will be uploaded as assets using the parameters supplied in `payload['process']['output_options']` (see cirruslib.transfer.upload_item_assets)

## Development

Tasks can be run locally as they include a CLI:

```
$ task.py -h
```

When run in Cirrus the `cirrus` subcommand is used when invoking Batch

```
$ task.py cirrus s3://bucket/prefix/payload.json
```

While when run locally use the `local` subcommand, specify a local payload, and optionally provide a working directory

```
$ task.py local tests/payload.json --workdir tests/
```

When run locally the handler will not upload assets to s3. It will also not remove the working directory when it completes.


## About

Cirrus is an open-source pipeline for processing geospatial data in AWS. Cirrus was developed by [Element 84](https://element84.com/) originally under a [NASA ACCESS project]. It is released under the Apache License.
