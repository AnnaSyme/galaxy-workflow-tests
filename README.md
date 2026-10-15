**Galaxy workflow tests**

[![Test workflows](https://github.com/AnnaSyme/galaxy-workflow-tests/actions/workflows/test-workflows.yml/badge.svg)](https://github.com/AnnaSyme/galaxy-workflow-tests/actions/workflows/test-workflows.yml)

Automatic tests for the Galaxy workflows by Anna Syme. Each test runs the workflow on real data on Galaxy Australia and checks that it still works.

**What is tested**

One `.ga` workflow file and one Planemo test file per workflow, in `workflows/`. The badge above shows the result of the last run. The reports, the logs and the pass or fail result of each run are in the Actions tab.

| Workflow | Source | Files |
|---|---|---|
| QC of Illumina data | Galaxy Australia, user annasyme | `workflows/ga-annasyme_qc-of-illumina-data.ga` |
| What is in my sequencing reads? | Galaxy Australia, user annasyme | `workflows/ga-annasyme_what-is-in-my-reads.ga` |
| Repeat masking - TSI | WorkflowHub 875, Version 3 | `workflows/wfh-875_repeat-masking-tsi.ga` |

**How it works**

A GitHub Action (`.github/workflows/test-workflows.yml`) installs Planemo and runs `planemo test` with the external Galaxy engine. Planemo uploads the test data to usegalaxy.org.au, runs the workflow in a test account, and checks each output. Galaxy does the computing, not GitHub: these workflows need tools and reference data that are only on Galaxy Australia.

Pass rule: all jobs finish without error, and every output exists and is not empty.

The Action runs by hand only (Run workflow in the Actions tab). A monthly schedule is possible later, with the agreement of Galaxy Australia.

**Test data**

Very small subsets, 4 MB or less, so that the tests are quick and the load on Galaxy Australia is low. Each test file gives the URL of each input dataset. The data is held in the Galaxy Australia test account and is readable by link.

**How to add a workflow**

1. Put the `.ga` file in `workflows/`.
2. Put a Planemo test file next to it, named `<ga file name>-tests.yml`. Planemo finds the test file by this name.
3. In the test file, give a URL for each input and an assertion for each output.
4. Add the workflow name to the `workflow` choice list in `.github/workflows/test-workflows.yml`.

**Setup**

The Action needs one repository secret, `GALAXY_API_KEY`: the API key of the Galaxy Australia test account.

**Credits**

Workflows by Anna Syme (ORCID [0000-0002-9906-0673](https://orcid.org/0000-0002-9906-0673)). Repeat masking - TSI is by Anna Syme and Luke Silver. Tests run on [Galaxy Australia](https://usegalaxy.org.au), a service of the Australian BioCommons and its partners.
