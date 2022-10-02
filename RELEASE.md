# Release
* Create new branch and PR
* Run PyCharm code inspection
* Run `$ pre-commit -all`
* Bump the version with `$ poetry version x.x.x`
* Export requirements `$ poetry export -o requirements.txt`
* Commit changes and push
* When CI is successful merge the PR
* Create release in Github
* Publish to pypi `$ poetry publish`