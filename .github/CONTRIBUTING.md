# Inkycal Contribution Policy

Thanks for wanting to contribute to the Inkycal Software!

Please note that in respect to Git-Flow and best practices of a good software, no Pull-Request (PR) apart from hotfixes may be merged into the /main branch. We do this to ensure stability and reliability. Ideally PRs should be directed to the development branch. Please also ensure your code is thoroughly tested before opening a PR. 
Lastly, don't forget to add your name to the file `CONTRIBUTORS.md`. Thank You!

PRs are not 100% guaranteed to be merged. Here are a few reasons, please do not take them personally:
- The code changes in the PR are too big, usually because it doesn't aim to fix a single thing, but a whole bunch of them. For developers, this may be a nightmare for testing.
- The code changes may not be too big, but with respect to the [Zen of Python](https://www.python.org/dev/peps/pep-0020/#the-zen-of-python), it may not be merged.
- The code changes are all good and small, but merging them leads to conflicts with other parts of the software. This too isn't intended.
- The code changes seemed to work well, but when the developers tested the code, they found additional bugs or unexpected behaviour.
- The code changes are all well, but the code is written in a way which will prove difficult for the maintainer to further maintain this code.

So, how should a PR look then to have better chances of merging?
- When creating the PR, use the development branch as your target, unless it fixes a critical issue in main.
- Keep it simple and short. Reading through the diff of several hundred lines makes things really hard to debug.
- Whenever possible, do not add dependencies. This makes things easier to integrate.
- Do not hesitate to open 5 or even 10 PRs for various suggestions if you need them. A single compact PR is very less likely to be merged.
- Don't forget to use comments! Comments make life so much easier for other developers who read your code for the first time. Explain what it does.

Even if all these rules are followed, PRs may take some time to be merged and reviewed. This is because PRs require the full attention of the developer, one line or even incorrect character may be enough to break the software, therefore PRs have to be tested by the maintainers. Sometimes they are busy for weeks (e.g. exams) and sometimes a PR might get merged in a single day. Please kep in mind that developers are human too and be nice to them :)
