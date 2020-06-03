<<<<<<< HEAD
# interagent
=======
# Python Project Simple Template

## pakcage requirement

```
├── requirements
│   ├── base.txt       # project base pakcage
│   ├── local.txt      # project develop pakcage
│   └── production.txt # production package
└── requirements.txt   # production package
```


## private packages

`packages` folder save private packages. You can use like this in requirement.txt

```
django==3.0.1
# ...

./packages/example.tgz
```

## environment recommaned
1. [pyenv](https://github.com/pyenv/pyenv)
if you are using MacOS with homebrew, maybe you need to install with commands:
```bash
brew install pyenv
brew install pyenv-virtualenv
pyenv install 3.8.2
```
then
```bash
make pyenv-3.8.2
```

##  pre-commit
You can use `pre-commit install` to init your pre-commit env, link and format your code when commit.

## Debug
### Step1:
run all dependencies services for eam-bk project
```bash
make up
```

### Step2:
if you want debug in container:
- **uncomment** docker-compose.yml file's backend service, maybe you need to change nginx backend upstream, finally `make up`

if you want debug in local
- use `make pyenv-3.8.2` to prepare your development environment 
- use `make migrate` to migrate table and init data
- **add** project interpreter to ide and **edit** debug configuration to debug eam-bk project(python main.py), maybe you need to config `READ_DOT_ENV_FILE` env in your ide

### Step3:
if you debug with web, open [eam](http://localhost:8061) in browser
if you debug with graphql playground, open [eam-bk](http://localhost:8000/graphql/) in browser or load .graphqlconfig by graphql-playground


## Develop
- if you has changed db model, use `make migrations-<your comments>` to generate migrations files, and use `make migrate` to migrate changes to db

- if you debug with graphql playground, maybe you need to use `make gqlg-schema` (npm install gql-generator -g) to generate graphql queries, mutations and subscriptions in dist/graphql/schema directory

- if you need build and push your image, use `make build` and `make push` to build your image in local and push your image to harbor(repo privileges required)

- if you has changed schema, change `app/types.py` by `make gen` result file


## test
- use `make gqlgt-schema` to generate or update schema for test usage
- if you need to test your code, use `make test`
- if you need to debug your test case, config your pytest env in your ide


## Reference
[github action for python](https://help.github.com/en/actions/language-and-framework-guides/using-python-with-github-actions)
[github action caching dependencies](https://help.github.com/en/actions/configuring-and-managing-workflows/caching-dependencies-to-speed-up-workflows)
[github action environment](https://help.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables)
[pytest and mock](https://medium.com/@bfortuner/python-unit-testing-with-pytest-and-mock-197499c4623c)
[Async fixtures with pytest](https://stackoverflow.com/questions/49936724/async-fixtures-with-pytest)
[create pg db](https://stackoverflow.com/questions/34484066/create-a-postgres-database-using-python/34484185)
[pytest env](https://stackoverflow.com/questions/36141024/how-to-pass-environment-variables-to-pytest)
>>>>>>> ccaa4ec... first commit
