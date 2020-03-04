These are guidelines for our core contributors to standardize our review
process and maintain a clean and readable git history.

We encourage newcomers not to worry so much about these practices --
above all, we want to make it easy for new contributors to get started.
Then we'll help you bring your pull request to fit our standards.

## Contributing

* We want to link contributions to open issues
  * It's good practice to open an issue before creating a PR if one doesn't
    already exist
  * This is intended to encourage discussion of a problem before looking at a
	solution's implementation
  * We should link to an issue in the commit message (e.g., `fixes #2`)
* We require all contributions to undergo a review process before being merged
  into the master branch
  * This includes contributions made by core contributors
    with push access to the GitHub repository
* We strongly refer pull requests to be atomic
  * That is, all changes should be directly related
  * Ideally each pull request will only change one thing
  * We encourage our core contributors to ask the author of a pull request to
	split it into multiple PRs if appropriate
* We want pull requests to have meaningful titles and descriptions
  * Often these can come from the first and subsequent lines
    of the commit message
  * See the commit message guidelines below

### Commit message structure

We want commit messages to be meaningful and follow a uniform formatting

  * The first line should contain a short summary of the commit
    * It should complete the sentence "If applied, this commit will ..."
	* It should be worded as a command or instruction
	  (This is called the "imperative mood)
	* The [article](https://chris.beams.io/posts/git-commit/) linked below
	  goes into much more detail and contains illustrative examples
  * The first line should be short (no more than 50 characters)
  * The first line should be capitalized
  * The first line shold never end with period
  * The first line should be separated from the body with a blank line
  * The body (everything after the first line)
    should be wrapped at 72 characters
  * The body should explain what was done, rather than how it was done
    * Note that the body need not use the imperative moood


We've adapted these guidelines from a somewhat canonical article:
https://chris.beams.io/posts/git-commit/

Example commit message:

	Add a guide for core contributors

    * Made sure to mention newcomers are not meant to worry
	  much about all these guidelines
    * Tried to be friendly rather than demanding

	Fixes #13



## Merging Pull Requests

* We'll squash and merge rather than simply merge
  * Squashing refers to combining all commits in a PR into one
  * This requires the individual merging the commit to create a new commit
	message
	* We'll follow the GitHub convention of referencing the PR
	  in parentheses
	  at the end of the first line of the commit message
  * We've configured the repository to allow only
    the squash and merge option in pull requests
  * These choices keep our git history much more clean than merges or multiple
	commits coming from a single pull request

