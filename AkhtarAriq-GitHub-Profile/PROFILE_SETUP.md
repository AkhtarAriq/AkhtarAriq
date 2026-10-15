# Set up Ariq's GitHub profile

This package contains a profile README and a lowlighter/metrics workflow. It has not been published to GitHub. The profile repository could not be retrieved during preparation; GitHub returned 404 for `AkhtarAriq/AkhtarAriq`.

## 1. Create or open the profile repository

Create a **public** repository owned by **AkhtarAriq**, named exactly **AkhtarAriq**:

https://github.com/new?name=AkhtarAriq

If this repository already exists, open it and check that the connected GitHub app has access. Review and merge these files with its existing content instead of replacing that content blindly.

## 2. Add the files

Extract the ZIP. Put these files at these exact repository paths, on the default branch:

- `README.md`
- `.github/workflows/metrics.yml`
- `github-metrics.svg`

`PROFILE_SETUP.md` is optional and does not need to be uploaded.

For the workflow, GitHub's **Add file → Create new file** is a reliable way to preserve the hidden `.github` directory: enter `.github/workflows/metrics.yml` as the filename, paste the supplied YAML, and commit. Upload the README and SVG to the repository root.

The SVG is an explicitly labeled setup placeholder, not simulated statistics. The workflow replaces it with real account data.

## 3. Create the Metrics token

Open https://github.com/settings/tokens and create a **classic personal access token** named `Profile Metrics` with a suitable expiration. For the public profile, languages, and contribution-calendar configuration in this package, the upstream documentation specifies a token **with no scopes selected**. Do not enable `repo` or organization access for this setup.

Copy the token directly into a GitHub repository secret. Do not paste it into the README, YAML, chat, or a commit.

The data-reading token and commit token are separate: `METRICS_TOKEN` reads public account data; the automatically supplied `GITHUB_TOKEN` writes the generated SVG to this repository.

## 4. Add the repository secret

Open the repository's **Settings → Secrets and variables → Actions → New repository secret**:

- Name: `METRICS_TOKEN`
- Secret: the personal access token from step 3

Direct link after the repository exists:

https://github.com/AkhtarAriq/AkhtarAriq/settings/secrets/actions

## 5. Generate the first card

Open **Actions → Profile metrics → Run workflow**, select the default branch, and run it.

https://github.com/AkhtarAriq/AkhtarAriq/actions

Wait for the run to finish successfully and commit `github-metrics.svg`, then refresh your profile. The README appears on the profile as soon as it is committed to the public username-matching repository. The real metrics appear after the workflow succeeds.

Daily updates are scheduled for **07:17 WIB / Asia/Jakarta**. GitHub can delay scheduled runs. Keep the workflow on the default branch. GitHub can disable schedules in inactive public repositories; re-enable the workflow in Actions if needed.

## Troubleshooting

- **Invalid/expired token:** replace the `METRICS_TOKEN` secret and rerun.
- **Write denied:** confirm Actions are allowed and repository or organization policy permits the job's `contents: write` permission. If the default branch requires pull requests, the workflow's direct SVG commit will need an approved alternative such as a dedicated output branch.
- **Placeholder remains:** inspect the latest Actions run, confirm the filename is `github-metrics.svg`, and refresh after the commit completes.
- **Language chart differs from your own contributions:** default language metrics summarize repository languages; they are not a measurement of proficiency or individual lines authored. This setup avoids the slower indepth repository-cloning mode.

## Validation and limits

The package is checked locally for YAML structure, supported Metrics inputs, SVG validity, matching image paths, and ZIP integrity. It cannot be run end to end until the repository and secret exist. The workflow uses upstream's documented stable `@latest` reference, which receives upstream updates.

## Official references

- Metrics: https://github.com/lowlighter/metrics
- Action setup: https://github.com/lowlighter/metrics/blob/latest/.github/readme/partials/documentation/setup/action.md
- Languages plugin: https://github.com/lowlighter/metrics/blob/latest/source/plugins/languages/README.md
- Isometric calendar: https://github.com/lowlighter/metrics/blob/latest/source/plugins/isocalendar/README.md

Profile content and project descriptions are editable. Add your portfolio and preferred contact links once you have confirmed the public URLs you want to share.
