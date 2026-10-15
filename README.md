**Galaxy workflow tests**

[![Test workflows](https://github.com/AnnaSyme/galaxy-workflow-tests/actions/workflows/test-workflows.yml/badge.svg)](https://github.com/AnnaSyme/galaxy-workflow-tests/actions/workflows/test-workflows.yml)

This repository checks that Galaxy workflows by Anna Syme still work.

For each workflow, it gets the published version, runs it on [Galaxy Australia](https://usegalaxy.org.au) with small test data, and checks the results. A workflow passes when every job finishes without an error and every output exists and is not empty.

Each run also lists any tool that Galaxy ran at a different version than the workflow asks for. This is a warning only: the jobs can still pass, but the results can differ.

**Workflows tested**

| Workflow | Published on |
|---|---|
| QC of Illumina data | Galaxy Australia |
| What is in my sequencing reads? | Galaxy Australia |
| Repeat masking - TSI | WorkflowHub (875) |

**See the results**

Open the [Actions tab](https://github.com/AnnaSyme/galaxy-workflow-tests/actions) and click the latest run. Each workflow shows pass or fail, with a short summary. The full report for each workflow is under Artifacts at the bottom of the run page.

**How it works**

1. `workflows.yml` lists each workflow and where it is published.
2. A GitHub Action downloads each workflow from that place, so the test uses the same version that people import.
3. [Planemo](https://planemo.readthedocs.io) runs the workflow on Galaxy Australia in a test account, with the test file in `tests/`.
4. After a pass, the Action removes the test history from the test account. After a fail, it keeps the history so the failed jobs can be checked.

The test data is in a history in the test account. Each test file has a link to each input file.

**Add a workflow**

1. Add the workflow to `workflows.yml`.
2. Add a test file, `tests/<name>-tests.yml`, with a link to each input file and a check for each output.

**Related work**

This repository is an interim setup for routine testing of these workflows. A broader workflow checker is in development separately, as joint work with [@mthang](https://github.com/mthang): [galaxy-workflow-validation](https://github.com/mthang/galaxy-workflow-validation). That project adds static checks of the workflow file and of the tools installed on a Galaxy server. The tool version check here draws on it.

**Credits**

Workflows by Anna Syme ([ORCID 0000-0002-9906-0673](https://orcid.org/0000-0002-9906-0673)). Repeat masking - TSI is by Anna Syme and Luke Silver. Galaxy Australia is a service of the Australian BioCommons and its partners.
