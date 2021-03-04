# Live League of Legends API reader

Python Script for watching live info from esports league of legends events.

Based on this [API](https://vickz84259.github.io/lolesports-api-docs/)

## Usage:

Get schedule for the upcoming esports events:

```shell
$ python api_reader.py -s
```

Get current live events:

```shell
$ python api_reader.py -l
```

Get event games:

```shell
$ python api_reader.py -e [EVENT_ID]
```

Watch a game through the API reader:

```shell
$ python api_reader.py -g [GAME_ID]
```

To see the commands and explanation:

```shell
$ python api_reader.py -h
```
