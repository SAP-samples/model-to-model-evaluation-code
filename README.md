[![REUSE status](https://api.reuse.software/badge/github.com/SAP-samples/model-to-model-evaluation-code
)](https://api.reuse.software/info/github.com/SAP-samples/model-to-model-evaluation-code
)

# BPMN model to model evaluation

## Description
This repository contains code for a multiset, model to model evaluation method for bpmn models.
The evaluation method is based on semantic similarity of multisets within a bpmn model and stems from this [master thesis](https://github.com/SAP-samples/multimodal-generative-ai-for-bpm).


## Requirements and set up

The requirements are in this [pyproject.toml](./pyproject.toml) file. After cloning the repository, run:

```shell
poetry install
```

## Getting started

This [notebook](./notebooks/code_usage.ipynb) shows how the evaluation module can be used to obtain a model to model similarity score. At a first step Signavio json models will be parsed into a minimal json format following this minimal bpmn [schema](./bpmn_schema.py.)

Multisets will then be extracted from the minimal json and a semantic similarity score will be calculated.\
The similarity score is an adjusted dice or jaccard set similarity score.

## Known Issues
No known issue.

## How to obtain support
[Create an issue](https://github.com/SAP-samples/model-to-model-evaluation-code/issues) in this repository if you find a bug or have questions about the content.



## Contributing
If you wish to contribute code, offer fixes or improvements, please send a pull request. Due to legal reasons, contributors will be asked to accept a DCO when they create the first pull request to this project. This happens in an automated fashion during the submission process. SAP uses [the standard DCO text of the Linux Foundation](https://developercertificate.org/).

## License
Copyright (c) 2024 SAP SE or an SAP affiliate company. All rights reserved. This project is licensed under the Apache Software License, version 2.0.

