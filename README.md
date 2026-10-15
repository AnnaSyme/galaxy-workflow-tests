**Galaxy workflow tests**

[![Test workflows](https://github.com/AnnaSyme/galaxy-workflow-tests/actions/workflows/test-workflows.yml/badge.svg)](https://github.com/AnnaSyme/galaxy-workflow-tests/actions/workflows/test-workflows.yml)

Automatic tests for the Galaxy workflows by Anna Syme. Each test downloads the published workflow from WorkflowHub or Galaxy Australia, runs it on small test data on Galaxy Australia, and checks every output. A pass means that the version the public imports works.

**What is tested**

| Workflow | Source |
|---|---|
| QC of Illumina data | Galaxy Australia, published by annasyme |
| What is in my sequencing reads? | Galaxy Australia, published by annasyme |
| Repeat masking - TSI | WorkflowHub 875 |

The full list, with IDs and versions, is in `workflows.yml`. Results for each run are in the Actions tab: a summary per workflow, plus HTML and JSON reports.

**How it works**

1. `workflows.yml` lists each workflow: source, ID, and version (latest, or a fixed version).
2. The Action (`.github/workflows/test-workflows.yml`) downloads each workflow from its source without a key, so only public workflows can be tested.
3. Planemo runs the workflow on usegalaxy.org.au in a test account, with the test file `tests/<name>-tests.yml`, and checks each output.
4. After a pass, the Action purges the test history and deletes the workflow copy that Planemo imported, so the test account does not fill up. After a fail, both are kept for inspection.

Galaxy does the computing, not GitHub: the workflows need tools and reference data that are on Galaxy Australia. Pass rule: all jobs finish without error, and every output exists and is not empty. A maximum of 2 workflows run at a time. The Action runs by hand only (Run workflow in the Actions tab); a schedule needs the agreement of Galaxy Australia.

**Test data**

Very small files, in a history in the Galaxy Australia test account. Each test file gives the URL of each input.

**How to add a workflow**

1. Add an entry to `workflows.yml`.
2. Add `tests/<name>-tests.yml`: a URL for each input and an assertion for each output.
3. Run the Action with that name.

**Setup**

One repository secret, `GALAXY_API_KEY`: the API key of the Galaxy Australia test account.

**Credits**

Workflows by Anna Syme (ORCID [0000-0002-9906-0673](https://orcid.org/0000-0002-9906-0673)). Repeat masking - TSI is by Anna Syme and Luke Silver. Tests run on [Galaxy Australia](https://usegalaxy.org.au), a service of the Australian BioCommons and its partners.
