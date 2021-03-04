# Live League of Legends API reader

Python Script for watching live info from esports league of legends events

## Usage:

Get schedule for the upcoming esports events:

```shell
$ python runner.py -gse
```

Get current live events:

```shell
$ python runner.py -gle
```

Get event games:

```shell
$ python runner.py -geg [EVENT_ID]
```

Watch a game through the API reader:

```shell
$ python runner.py -wg [GAME_ID]
```
