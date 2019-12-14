<p align="center">
  <img src="./Nostalgia-C.png" width="200px"/>
</p>

# nostalgia

[![PyPI](https://img.shields.io/pypi/v/nostalgia.svg?style=flat-square)](https://pypi.python.org/pypi/nostalgia/)
[![PyPI](https://img.shields.io/pypi/pyversions/nostalgia.svg?style=flat-square)](https://pypi.python.org/pypi/nostalgia/)

### Ecosystem for combining personal data

Nostalgia will help with gathering data from a variety of sources and enable you to combine them easily.

It's much like [Home Assistant](https://github.com/home-assistant/home-assistant), providing a platform, but then for connecting data instead of IoT devices.

Afterwards, it will help you filter and visualize the data.

The architecture is as follows.

You're looking at the core which contains the code for sources, installing the backend system and allows you to write scripts using Nostalgia Query Language.

If you want to add your own data that is not supported, please for now contact me directly in either [discord](https://discord.gg/nJQfM2A) or [slack](https://bit.ly/2Yre09N) and we'll help you get started.

### Nostalgia Query Language - based on pandas

```python
payments.expenses.by_card.last_week.office_days.at_night().heartrate_above(80).when_at("amsterdam").sum()
```

This will give the total expenses by card in the last week, but only on work days, at night, when my heart rate is above 80 and I'm in Amsterdam.
It combined the generic class functionality, together with data from:

- A Payments provider
- A Location provider
- A Heartrate provider

### Available Data Bindings

- Bank payments (ING)
- Heartrate (fitbit)
- Sleep (fitbit)
- Places (Google Timeline: scraped)
- Indoor positioning (whereami)
- Pictures (Google)
- Public transport (MijnOV)
- Chrome History (plugin)
  - Products (Chrome Page Views)
  - Events (Chrome Page Views)
- File visits (Emacs)
- Emails (gmail)


### Contributing

Please contribute the data sources that others could use as well!
